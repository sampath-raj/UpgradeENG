import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session_factory
from app.models.user import User
from app.models.writing import WritingSubmission
from app.models.curriculum import CurriculumDay
from app.schemas.features import (
    WritingSubmitRequest,
    WritingCorrectionResponse,
    CorrectionBlock,
    WritingHistoryItem,
)
from app.services.auth import get_current_user
from app.services import ai_coach

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/writing", tags=["writing"])
limiter = Limiter(key_func=get_remote_address)


async def _retry_correction(submission_id, user_text: str, writing_prompt: str):
    """Background task to retry AI correction if the initial call failed."""
    try:
        correction = await ai_coach.correct_writing(user_text, writing_prompt)
        async with async_session_factory() as db:
            result = await db.execute(
                select(WritingSubmission).where(WritingSubmission.id == submission_id)
            )
            sub = result.scalar_one_or_none()
            if sub:
                sub.correction_json = correction
                await db.commit()
                logger.info(f"Background correction succeeded for submission {submission_id}")
    except Exception as e:
        logger.error(f"Background correction retry failed: {e}")


@router.post("/submit", response_model=WritingCorrectionResponse)
@limiter.limit("10/minute")
async def submit_writing(
    request: Request,
    body: WritingSubmitRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit writing for AI correction. Saves immediately, then calls Claude."""
    # Get the writing prompt for context
    day_result = await db.execute(
        select(CurriculumDay).where(CurriculumDay.day_number == body.day_number)
    )
    day = day_result.scalar_one_or_none()
    writing_prompt = day.writing_prompt if day else "General writing"

    # Save submission immediately
    submission = WritingSubmission(
        user_id=user.id,
        day_number=body.day_number,
        original_text=body.text,
        correction_json=None,
    )
    db.add(submission)
    await db.flush()
    submission_id = submission.id

    # Try to get AI correction
    try:
        correction = await ai_coach.correct_writing(body.text, writing_prompt)
        submission.correction_json = correction
        await db.flush()
    except Exception as e:
        logger.warning(f"AI correction failed, scheduling retry: {e}")
        background_tasks.add_task(_retry_correction, submission_id, body.text, writing_prompt)
        correction = {
            "blocks": [{
                "original": body.text,
                "corrected": "",
                "natural": "",
                "reason": "AI feedback is being generated. Please refresh in a moment."
            }]
        }

    blocks = [CorrectionBlock(**b) for b in correction.get("blocks", [])]

    return WritingCorrectionResponse(
        id=submission_id,
        day_number=body.day_number,
        original_text=body.text,
        blocks=blocks,
        created_at=submission.created_at,
    )


@router.get("/history", response_model=list[WritingHistoryItem])
async def get_writing_history(
    day_number: int | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get user's writing submission history, optionally filtered by day."""
    query = select(WritingSubmission).where(
        WritingSubmission.user_id == user.id
    ).order_by(WritingSubmission.created_at.desc())

    if day_number is not None:
        query = query.where(WritingSubmission.day_number == day_number)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{submission_id}", response_model=WritingCorrectionResponse)
async def get_submission(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a specific writing submission with its correction."""
    result = await db.execute(
        select(WritingSubmission).where(
            WritingSubmission.id == UUID(submission_id),
            WritingSubmission.user_id == user.id,
        )
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    blocks = []
    if sub.correction_json and "blocks" in sub.correction_json:
        blocks = [CorrectionBlock(**b) for b in sub.correction_json["blocks"]]

    return WritingCorrectionResponse(
        id=sub.id,
        day_number=sub.day_number,
        original_text=sub.original_text,
        blocks=blocks,
        created_at=sub.created_at,
    )
