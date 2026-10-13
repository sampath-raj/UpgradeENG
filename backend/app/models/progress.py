import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserDayProgress(Base):
    __tablename__ = "user_day_progress"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    modules_completed: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "grammar": False,
            "vocabulary": False,
            "writing": False,
            "speaking": False,
            "mock_interview": False,
        },
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="day_progress")
