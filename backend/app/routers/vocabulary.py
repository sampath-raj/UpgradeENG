from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.vocabulary import VocabularyGroup, VocabPracticeEntry, VocabStatus
from app.schemas.curriculum import (
    VocabularyGroupResponse,
    VocabPracticeRequest,
    VocabPracticeResponse,
    VocabCheckMasteredRequest,
    VocabStatusResponse,
)
from app.services.auth import get_current_user
from app.services import ai_coach

router = APIRouter(prefix="/vocab", tags=["vocabulary"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/day/{day_number}", response_model=list[VocabularyGroupResponse])
async def get_vocab_for_day(
    day_number: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get all vocabulary groups for a specific day."""
    result = await db.execute(
        select(VocabularyGroup).where(VocabularyGroup.day_number == day_number)
    )
    return result.scalars().all()


@router.get("/review", response_model=list[VocabularyGroupResponse])
async def get_review_queue(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get vocabulary groups due for spaced-repetition review.
    Returns groups where the user has practiced but not yet mastered,
    from days older than the current day - 2.
    """
    current_day = user.current_day or 1

    # Get groups the user has practiced but not mastered
    practiced_result = await db.execute(
        select(VocabPracticeEntry.group_id).where(
            and_(
                VocabPracticeEntry.user_id == user.id,
                VocabPracticeEntry.status == VocabStatus.PRACTICED,
            )
        ).distinct()
    )
    practiced_group_ids = [row[0] for row in practiced_result.all()]

    if not practiced_group_ids:
        return []

    # Filter to groups from earlier days (spaced repetition)
    review_cutoff_day = max(1, current_day - 2)
    result = await db.execute(
        select(VocabularyGroup).where(
            and_(
                VocabularyGroup.id.in_(practiced_group_ids),
                VocabularyGroup.day_number <= review_cutoff_day,
            )
        ).limit(10)
    )
    return result.scalars().all()


@router.post("/practice", response_model=VocabPracticeResponse)
async def practice_vocab(
    body: VocabPracticeRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit a practice sentence for a vocabulary group."""
    # Verify group exists
    group_result = await db.execute(
        select(VocabularyGroup).where(VocabularyGroup.id == body.group_id)
    )
    group = group_result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Vocabulary group not found")

    # Upsert: check for an existing entry for this user+group
    existing_result = await db.execute(
        select(VocabPracticeEntry).where(
            and_(
                VocabPracticeEntry.user_id == user.id,
                VocabPracticeEntry.group_id == body.group_id,
            )
        ).limit(1)
    )
    entry = existing_result.scalar_one_or_none()

    if entry:
        # Update the existing entry's sentence (keep its current status)
        entry.user_sentence = body.user_sentence
    else:
        entry = VocabPracticeEntry(
            user_id=user.id,
            group_id=body.group_id,
            user_sentence=body.user_sentence,
            status=VocabStatus.PRACTICED,
        )
        db.add(entry)

    await db.flush()

    return VocabPracticeResponse(
        id=entry.id,
        group_id=entry.group_id,
        user_sentence=entry.user_sentence,
        status=entry.status.value if hasattr(entry.status, 'value') else entry.status,
    )


@router.post("/check-mastered", response_model=VocabStatusResponse)
@limiter.limit("15/minute")
async def check_mastered(
    request: Request,
    body: VocabCheckMasteredRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Check if the user's sentence demonstrates mastery of the vocab group."""
    group_result = await db.execute(
        select(VocabularyGroup).where(VocabularyGroup.id == body.group_id)
    )
    group = group_result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Vocabulary group not found")

    # Call AI to check
    result = await ai_coach.check_vocab_mastery(
        body.user_sentence, group.headword, group.phrases
    )

    is_correct = result.get("is_correct", False)
    feedback = result.get("feedback", "")

    if is_correct:
        # Count existing correct uses BEFORE adding the new one
        correct_count_result = await db.execute(
            select(VocabPracticeEntry).where(
                and_(
                    VocabPracticeEntry.user_id == user.id,
                    VocabPracticeEntry.group_id == body.group_id,
                )
            )
        )
        existing_entries = correct_count_result.scalars().all()
        existing_count = len(existing_entries)

        # Upsert or add a new practice entry for this correct use
        if existing_entries:
            # Update the latest entry with the new correct sentence
            existing_entries[-1].user_sentence = body.user_sentence
            existing_entries[-1].status = VocabStatus.PRACTICED
        else:
            new_entry = VocabPracticeEntry(
                user_id=user.id,
                group_id=body.group_id,
                user_sentence=body.user_sentence,
                status=VocabStatus.PRACTICED,
            )
            db.add(new_entry)
        await db.flush()

        # Mastery requires 2 distinct correct uses (existing_count was 0-based before this call)
        if existing_count >= 1:
            # Promote all entries to mastered
            for e in existing_entries:
                e.status = VocabStatus.MASTERED
            await db.flush()

            return VocabStatusResponse(
                group_id=body.group_id,
                status="mastered",
                is_mastered=True,
                feedback=f"Excellent! You've mastered this group. {feedback}",
            )

        return VocabStatusResponse(
            group_id=body.group_id,
            status="practiced",
            is_mastered=False,
            feedback=f"Good use! One more correct example will mark this as mastered. {feedback}",
        )

    return VocabStatusResponse(
        group_id=body.group_id,
        status="not_started",
        is_mastered=False,
        feedback=feedback,
    )


@router.get("/status", response_model=dict)
async def get_vocab_status(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get overall vocabulary progress for the user."""
    # Total groups
    total_result = await db.execute(select(VocabularyGroup))
    total_groups = len(total_result.scalars().all())

    # Practiced
    practiced_result = await db.execute(
        select(VocabPracticeEntry.group_id).where(
            VocabPracticeEntry.user_id == user.id
        ).distinct()
    )
    practiced_count = len(practiced_result.all())

    # Mastered
    mastered_result = await db.execute(
        select(VocabPracticeEntry.group_id).where(
            and_(
                VocabPracticeEntry.user_id == user.id,
                VocabPracticeEntry.status == VocabStatus.MASTERED,
            )
        ).distinct()
    )
    mastered_count = len(mastered_result.all())

    return {
        "total_groups": total_groups,
        "practiced": practiced_count,
        "mastered": mastered_count,
    }
