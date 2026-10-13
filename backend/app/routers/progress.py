from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.mock_interview import MockInterview, InterviewType
from app.models.vocabulary import VocabPracticeEntry, VocabStatus, VocabularyGroup
from app.models.writing import WritingSubmission
from app.models.progress import UserDayProgress
from app.schemas.features import (
    ProgressSummary,
    ScoreTrendPoint,
    ScoreDetail,
    ComparisonResponse,
    MockInterviewFinishResponse,
    ChatMessage,
    DayProgressUpdate,
)
from app.services.auth import get_current_user

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/summary", response_model=ProgressSummary)
async def get_progress_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get overall progress summary."""
    # Days completed
    days_result = await db.execute(
        select(func.count()).select_from(UserDayProgress).where(
            and_(
                UserDayProgress.user_id == user.id,
                UserDayProgress.completed_at.isnot(None),
            )
        )
    )
    days_completed = days_result.scalar() or 0

    # Vocab stats
    total_groups_result = await db.execute(
        select(func.count()).select_from(VocabularyGroup)
    )
    total_groups = total_groups_result.scalar() or 0

    mastered_result = await db.execute(
        select(VocabPracticeEntry.group_id).where(
            and_(
                VocabPracticeEntry.user_id == user.id,
                VocabPracticeEntry.status == VocabStatus.MASTERED,
            )
        ).distinct()
    )
    mastered_count = len(mastered_result.all())

    # Writing count
    writing_result = await db.execute(
        select(func.count()).select_from(WritingSubmission).where(
            WritingSubmission.user_id == user.id
        )
    )
    writing_count = writing_result.scalar() or 0

    # Mock interviews count
    interview_result = await db.execute(
        select(func.count()).select_from(MockInterview).where(
            and_(
                MockInterview.user_id == user.id,
                MockInterview.scores_json.isnot(None),
            )
        )
    )
    interview_count = interview_result.scalar() or 0

    return ProgressSummary(
        current_day=user.current_day,
        streak_count=user.streak_count,
        days_completed=days_completed,
        vocab_groups_mastered=mastered_count,
        vocab_groups_total=total_groups,
        writing_submissions=writing_count,
        mock_interviews_completed=interview_count,
    )


@router.get("/trend", response_model=list[ScoreTrendPoint])
async def get_score_trend(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get mock interview score trend over time."""
    result = await db.execute(
        select(MockInterview).where(
            and_(
                MockInterview.user_id == user.id,
                MockInterview.scores_json.isnot(None),
            )
        ).order_by(MockInterview.day_number)
    )
    interviews = result.scalars().all()

    points = []
    for i in interviews:
        scores = i.scores_json or {}
        points.append(ScoreTrendPoint(
            day_number=i.day_number,
            interview_type=i.interview_type.value if hasattr(i.interview_type, 'value') else i.interview_type,
            scores=ScoreDetail(**scores),
            created_at=i.created_at,
        ))

    return points


@router.get("/comparison", response_model=ComparisonResponse)
async def get_comparison(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get Day 0 baseline vs Day 30 final interview comparison."""
    baseline_result = await db.execute(
        select(MockInterview).where(
            and_(
                MockInterview.user_id == user.id,
                MockInterview.interview_type == InterviewType.BASELINE,
            )
        ).order_by(MockInterview.created_at).limit(1)
    )
    baseline = baseline_result.scalar_one_or_none()

    final_result = await db.execute(
        select(MockInterview).where(
            and_(
                MockInterview.user_id == user.id,
                MockInterview.interview_type == InterviewType.FINAL,
            )
        ).order_by(MockInterview.created_at.desc()).limit(1)
    )
    final = final_result.scalar_one_or_none()

    def _to_response(interview):
        if not interview or not interview.scores_json:
            return None
        scores = ScoreDetail(**interview.scores_json)
        transcript = [ChatMessage(**m) for m in (interview.transcript_json or [])]
        return MockInterviewFinishResponse(
            interview_id=interview.id,
            scores=scores,
            feedback=interview.feedback or "",
            transcript=transcript,
        )

    return ComparisonResponse(
        baseline=_to_response(baseline),
        final=_to_response(final),
    )


@router.post("/day-complete")
async def mark_module_complete(
    body: DayProgressUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Mark a module as completed for a day and update streaks."""
    # Get or create day progress
    result = await db.execute(
        select(UserDayProgress).where(
            and_(
                UserDayProgress.user_id == user.id,
                UserDayProgress.day_number == body.day_number,
            )
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        progress = UserDayProgress(
            user_id=user.id,
            day_number=body.day_number,
            modules_completed={
                "grammar": False,
                "vocabulary": False,
                "writing": False,
                "speaking": False,
                "mock_interview": False,
            },
        )
        db.add(progress)
        await db.flush()

    # Update the specific module
    modules = dict(progress.modules_completed)
    modules[body.module] = True
    progress.modules_completed = modules

    # Check if all modules are complete
    required = ["grammar", "vocabulary", "writing", "speaking"]
    all_done = all(modules.get(m, False) for m in required)

    if all_done and not progress.completed_at:
        progress.completed_at = datetime.now(timezone.utc)

        # Update user's current day and streak
        if body.day_number >= user.current_day:
            user.current_day = body.day_number + 1

        # Update streak
        today = datetime.now(timezone.utc).date()
        if user.last_active_date:
            last_active = user.last_active_date.date() if hasattr(user.last_active_date, 'date') else user.last_active_date
            if (today - last_active).days <= 1:
                user.streak_count += 1
            elif (today - last_active).days > 1:
                user.streak_count = 1
        else:
            user.streak_count = 1

        user.last_active_date = datetime.now(timezone.utc)

    await db.flush()

    return {
        "day_number": body.day_number,
        "modules_completed": modules,
        "day_complete": all_done,
        "current_day": user.current_day,
        "streak_count": user.streak_count,
    }


@router.get("/days-status")
async def get_days_status(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get completion status for all days."""
    result = await db.execute(
        select(UserDayProgress).where(
            UserDayProgress.user_id == user.id
        ).order_by(UserDayProgress.day_number)
    )
    progress_list = result.scalars().all()

    return [
        {
            "day_number": p.day_number,
            "modules_completed": p.modules_completed,
            "completed_at": p.completed_at.isoformat() if p.completed_at else None,
        }
        for p in progress_list
    ]
