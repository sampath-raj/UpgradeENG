import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WritingSubmission(Base):
    __tablename__ = "writing_submissions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    correction_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="writing_submissions")
