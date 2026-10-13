from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ── Writing ──────────────────────────────────────────────────────────────────

class CorrectionBlock(BaseModel):
    original: str
    corrected: str
    natural: str
    reason: str


class WritingSubmitRequest(BaseModel):
    day_number: int
    text: str = Field(..., min_length=10, max_length=5000)


class WritingCorrectionResponse(BaseModel):
    id: str
    day_number: int
    original_text: str
    blocks: list[CorrectionBlock]
    created_at: datetime

    model_config = {"from_attributes": True}


class WritingHistoryItem(BaseModel):
    id: str
    day_number: int
    original_text: str
    correction_json: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Speaking ─────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class SpeakingChatRequest(BaseModel):
    day_number: int
    mode: str
    messages: list[ChatMessage]
    session_id: Optional[str] = None


class SpeakingChatResponse(BaseModel):
    session_id: str
    reply: str


class SpeakingEndRequest(BaseModel):
    session_id: str
    messages: list[ChatMessage]


# ── Mock Interview ───────────────────────────────────────────────────────────

class MockInterviewStartRequest(BaseModel):
    day_number: int
    interview_type: str = "weekly_checkpoint"  # baseline | weekly_checkpoint | final


class MockInterviewStartResponse(BaseModel):
    interview_id: str
    first_question: str


class MockInterviewRespondRequest(BaseModel):
    interview_id: str
    user_answer: str


class MockInterviewRespondResponse(BaseModel):
    next_question: Optional[str] = None
    is_complete: bool


class ScoreDetail(BaseModel):
    grammar: Optional[int] = None
    vocabulary: Optional[int] = None
    fluency: Optional[int] = None
    pronunciation: Optional[int] = None
    confidence: Optional[int] = None
    structure: Optional[int] = None
    overall: Optional[int] = None
    pronunciation_note: Optional[str] = "voice mode required"
    confidence_note: Optional[str] = "voice mode required"


class MockInterviewFinishRequest(BaseModel):
    interview_id: str


class MockInterviewFinishResponse(BaseModel):
    interview_id: str
    scores: ScoreDetail
    feedback: str
    transcript: list[ChatMessage]


# ── Progress ─────────────────────────────────────────────────────────────────

class DayProgressUpdate(BaseModel):
    day_number: int
    module: str  # grammar | vocabulary | writing | speaking | mock_interview


class ProgressSummary(BaseModel):
    current_day: int
    streak_count: int
    days_completed: int
    vocab_groups_mastered: int
    vocab_groups_total: int
    writing_submissions: int
    mock_interviews_completed: int


class ScoreTrendPoint(BaseModel):
    day_number: int
    interview_type: str
    scores: ScoreDetail
    created_at: datetime


class ComparisonResponse(BaseModel):
    baseline: Optional[MockInterviewFinishResponse] = None
    final: Optional[MockInterviewFinishResponse] = None
