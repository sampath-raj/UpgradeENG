from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.curriculum import CurriculumDay
from app.models.user import User
from app.schemas.curriculum import CurriculumDayResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


@router.get("/days", response_model=list[CurriculumDayResponse])
async def list_days(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all curriculum days with basic info (no heavy content for the overview)."""
    result = await db.execute(
        select(CurriculumDay).order_by(CurriculumDay.day_number)
    )
    days = result.scalars().all()
    return days


@router.get("/days/{day_number}", response_model=CurriculumDayResponse)
async def get_day(
    day_number: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get full details for a specific curriculum day, including vocab groups."""
    result = await db.execute(
        select(CurriculumDay).where(CurriculumDay.day_number == day_number)
    )
    day = result.scalar_one_or_none()
    if not day:
        raise HTTPException(status_code=404, detail=f"Day {day_number} not found")
    return day
