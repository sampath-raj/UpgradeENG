import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    current_day: Mapped[int] = mapped_column(Integer, default=0)
    streak_count: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    writing_submissions = relationship("WritingSubmission", back_populates="user", lazy="selectin")
    speaking_sessions = relationship("SpeakingSession", back_populates="user", lazy="selectin")
    mock_interviews = relationship("MockInterview", back_populates="user", lazy="selectin")
    vocab_practice_entries = relationship("VocabPracticeEntry", back_populates="user", lazy="selectin")
    day_progress = relationship("UserDayProgress", back_populates="user", lazy="selectin")
