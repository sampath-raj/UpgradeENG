from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CurriculumDay(Base):
    __tablename__ = "curriculum_days"

    day_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    week_theme: Mapped[str] = mapped_column(String(100), nullable=False)
    focus_topic: Mapped[str] = mapped_column(String(200), nullable=False)
    grammar_topic: Mapped[str] = mapped_column(String(200), nullable=False)
    grammar_lesson_md: Mapped[str] = mapped_column(Text, nullable=False, default="")
    speaking_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    writing_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    is_milestone_day: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    vocabulary_groups = relationship("VocabularyGroup", back_populates="curriculum_day", lazy="selectin")
