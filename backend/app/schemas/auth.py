import uuid
from datetime import datetime
from pydantic import BaseModel, Field


# ── Auth ─────────────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    current_day: int
    streak_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
