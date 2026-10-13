import uuid
from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Enum as SAEnum, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class VocabStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    PRACTICED = "practiced"
    MASTERED = "mastered"


class VocabularyGroup(Base):
    __tablename__ = "vocabulary_groups"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    day_number: Mapped[int] = mapped_column(
        Integer, ForeignKey("curriculum_days.day_number"), nullable=False, index=True
    )
    headword: Mapped[str] = mapped_column(String(100), nullable=False)
    phrases: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    example_sentences: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # Relationships
    curriculum_day = relationship("CurriculumDay", back_populates="vocabulary_groups")
    practice_entries = relationship("VocabPracticeEntry", back_populates="vocabulary_group", lazy="selectin")


class VocabPracticeEntry(Base):
    __tablename__ = "vocab_practice_entries"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    group_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("vocabulary_groups.id"), nullable=False, index=True
    )
    user_sentence: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(VocabStatus, name="vocab_status"),
        default=VocabStatus.PRACTICED,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="vocab_practice_entries")
    vocabulary_group = relationship("VocabularyGroup", back_populates="practice_entries")
