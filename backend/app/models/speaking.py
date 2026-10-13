import uuid
from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Enum as SAEnum, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SpeakingMode(str, enum.Enum):
    INTRO = "intro"
    UNPREPARED = "unprepared"
    INTERVIEW_QS = "interview_qs"
    FREE_CHAT = "free_chat"


class SpeakingSession(Base):
    __tablename__ = "speaking_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    mode: Mapped[str] = mapped_column(
        SAEnum(SpeakingMode, name="speaking_mode"),
        nullable=False,
    )
    transcript_json: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="speaking_sessions")
