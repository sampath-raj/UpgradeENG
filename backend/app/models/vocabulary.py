import uuid
from datetime import datetime

from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

import enum


class VocabStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    PRACTICED = "practiced"
    MASTERED = "mastered"


class VocabularyGroup(Base):
    __tablename__ = "vocabulary_groups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
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

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vocabulary_groups.id"), nullable=False, index=True
    )
    user_sentence: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(VocabStatus, name="vocab_status", create_constraint=True),
        default=VocabStatus.PRACTICED,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="vocab_practice_entries")
    vocabulary_group = relationship("VocabularyGroup", back_populates="practice_entries")
