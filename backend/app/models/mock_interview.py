import uuid
from datetime import datetime
import enum

from sqlalchemy import Integer, String, ForeignKey, DateTime, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class InterviewType(str, enum.Enum):
    BASELINE = "baseline"
    WEEKLY_CHECKPOINT = "weekly_checkpoint"
    FINAL = "final"


class MockInterview(Base):
    __tablename__ = "mock_interviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    interview_type: Mapped[str] = mapped_column(
        SAEnum(InterviewType, name="interview_type", create_constraint=True),
        nullable=False,
    )
    transcript_json: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    scores_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    feedback: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="mock_interviews")
