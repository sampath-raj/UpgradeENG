import uuid
from datetime import datetime
import enum

from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SpeakingMode(str, enum.Enum):
    INTRO = "intro"
    UNPREPARED = "unprepared"
    INTERVIEW_QS = "interview_qs"
    FREE_CHAT = "free_chat"


class SpeakingSession(Base):
    __tablename__ = "speaking_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    mode: Mapped[str] = mapped_column(
        SAEnum(SpeakingMode, name="speaking_mode", create_constraint=True),
        nullable=False,
    )
    transcript_json: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="speaking_sessions")
