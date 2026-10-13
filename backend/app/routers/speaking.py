import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.speaking import SpeakingSession, SpeakingMode
from app.models.curriculum import CurriculumDay
from app.schemas.features import (
    SpeakingChatRequest,
    SpeakingChatResponse,
    SpeakingEndRequest,
)
from app.services.auth import get_current_user
from app.services import ai_coach

router = APIRouter(prefix="/speaking", tags=["speaking"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/chat", response_model=SpeakingChatResponse)
@limiter.limit("20/minute")
async def speaking_chat(
    request: Request,
    body: SpeakingChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Chat with the AI coach in speaking practice mode."""
    # Get day context
    day_result = await db.execute(
        select(CurriculumDay).where(CurriculumDay.day_number == body.day_number)
    )
    day = day_result.scalar_one_or_none()
    day_topic = day.focus_topic if day else "General conversation"

    # Convert messages to Claude format
    claude_messages = [
        {"role": m.role, "content": m.content}
        for m in body.messages
    ]

    # Get AI reply
    reply = await ai_coach.speaking_chat(claude_messages, day_topic, body.mode)

    # Create or update session
    session_id = body.session_id or str(uuid.uuid4())

    if body.session_id:
        # Update existing session
        result = await db.execute(
            select(SpeakingSession).where(SpeakingSession.id == body.session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            transcript = session.transcript_json or []
            transcript.append({"role": "user", "content": body.messages[-1].content})
            transcript.append({"role": "assistant", "content": reply})
            session.transcript_json = transcript
    else:
        # Create new session
        transcript = [
            {"role": m.role, "content": m.content}
            for m in body.messages
        ]
        transcript.append({"role": "assistant", "content": reply})

        session = SpeakingSession(
            id=session_id,
            user_id=user.id,
            day_number=body.day_number,
            mode=body.mode,
            transcript_json=transcript,
        )
        db.add(session)

    await db.flush()

    return SpeakingChatResponse(session_id=session_id, reply=reply)


@router.post("/end")
async def end_speaking_session(
    body: SpeakingEndRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """End a speaking session and save the final transcript."""
    result = await db.execute(
        select(SpeakingSession).where(
            SpeakingSession.id == body.session_id,
            SpeakingSession.user_id == user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.transcript_json = [
        {"role": m.role, "content": m.content} for m in body.messages
    ]
    await db.flush()

    return {"status": "ok", "session_id": str(session.id)}
