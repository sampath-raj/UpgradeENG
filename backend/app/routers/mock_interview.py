
from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.mock_interview import MockInterview, InterviewType
from app.schemas.features import (
    MockInterviewStartRequest,
    MockInterviewStartResponse,
    MockInterviewRespondRequest,
    MockInterviewRespondResponse,
    MockInterviewFinishRequest,
    MockInterviewFinishResponse,
    ScoreDetail,
    ChatMessage,
)
from app.services.auth import get_current_user
from app.services import ai_coach

router = APIRouter(prefix="/mock-interview", tags=["mock-interview"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/start", response_model=MockInterviewStartResponse)
@limiter.limit("5/minute")
async def start_interview(
    request: Request,
    body: MockInterviewStartRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Start a new mock interview session."""
    # Map string to enum
    interview_type = InterviewType(body.interview_type)

    # Get first question from AI
    first_question = await ai_coach.interview_ask([], body.interview_type, body.day_number)

    # Create interview record
    interview = MockInterview(
        user_id=user.id,
        day_number=body.day_number,
        interview_type=interview_type,
        transcript_json=[{"role": "assistant", "content": first_question}],
    )
    db.add(interview)
    await db.flush()

    return MockInterviewStartResponse(
        interview_id=interview.id,
        first_question=first_question,
    )


@router.post("/respond", response_model=MockInterviewRespondResponse)
@limiter.limit("30/minute")
async def respond_to_interview(
    request: Request,
    body: MockInterviewRespondRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send user's answer and get the next question."""
    result = await db.execute(
        select(MockInterview).where(
            and_(
                MockInterview.id == body.interview_id,
                MockInterview.user_id == user.id,
            )
        )
    )
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Add user's answer to transcript
    transcript = interview.transcript_json or []
    transcript.append({"role": "user", "content": body.user_answer})

    # Get next question
    interview_type_str = (
        interview.interview_type.value
        if hasattr(interview.interview_type, "value")
        else interview.interview_type
    )
    next_response = await ai_coach.interview_ask(
        transcript, interview_type_str, interview.day_number
    )

    is_complete = "[INTERVIEW_COMPLETE]" in next_response

    if not is_complete:
        transcript.append({"role": "assistant", "content": next_response})

    interview.transcript_json = transcript
    await db.flush()

    return MockInterviewRespondResponse(
        next_question=next_response if not is_complete else None,
        is_complete=is_complete,
    )


@router.post("/finish", response_model=MockInterviewFinishResponse)
@limiter.limit("5/minute")
async def finish_interview(
    request: Request,
    body: MockInterviewFinishRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Score a completed mock interview."""
    result = await db.execute(
        select(MockInterview).where(
            and_(
                MockInterview.id == body.interview_id,
                MockInterview.user_id == user.id,
            )
        )
    )
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    transcript = interview.transcript_json or []

    # Get scores from AI
    scores_data = await ai_coach.interview_score(transcript)

    # Save scores
    interview.scores_json = {
        "grammar": scores_data.get("grammar"),
        "vocabulary": scores_data.get("vocabulary"),
        "fluency": scores_data.get("fluency"),
        "pronunciation": None,
        "confidence": None,
        "structure": scores_data.get("structure"),
        "overall": scores_data.get("overall"),
        "pronunciation_note": "voice mode required",
        "confidence_note": "voice mode required",
    }
    interview.feedback = scores_data.get("feedback", "")
    await db.flush()

    scores = ScoreDetail(**interview.scores_json)
    chat_messages = [ChatMessage(**m) for m in transcript]

    return MockInterviewFinishResponse(
        interview_id=interview.id,
        scores=scores,
        feedback=interview.feedback or "",
        transcript=chat_messages,
    )


@router.get("/list")
async def list_interviews(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all mock interviews for the user."""
    result = await db.execute(
        select(MockInterview).where(
            MockInterview.user_id == user.id
        ).order_by(MockInterview.created_at.desc())
    )
    interviews = result.scalars().all()
    return [
        {
            "id": str(i.id),
            "day_number": i.day_number,
            "interview_type": i.interview_type.value if hasattr(i.interview_type, 'value') else i.interview_type,
            "scores_json": i.scores_json,
            "feedback": i.feedback,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        }
        for i in interviews
    ]
