from typing import Optional
from pydantic import BaseModel


class CurriculumDayResponse(BaseModel):
    day_number: int
    week_number: int
    week_theme: str
    focus_topic: str
    grammar_topic: str
    grammar_lesson_md: str
    speaking_prompt: str
    writing_prompt: str
    is_milestone_day: bool
    vocabulary_groups: list["VocabularyGroupResponse"] = []

    model_config = {"from_attributes": True}


class VocabularyGroupResponse(BaseModel):
    id: str
    day_number: int
    headword: str
    phrases: list[str]
    example_sentences: list[str]

    model_config = {"from_attributes": True}


class VocabPracticeRequest(BaseModel):
    group_id: str
    user_sentence: str


class VocabPracticeResponse(BaseModel):
    id: str
    group_id: str
    user_sentence: str
    status: str
    feedback: Optional[str] = None

    model_config = {"from_attributes": True}


class VocabCheckMasteredRequest(BaseModel):
    group_id: str
    user_sentence: str


class VocabStatusResponse(BaseModel):
    group_id: str
    status: str
    is_mastered: bool
    feedback: Optional[str] = None
