"""
Seed script — populates CurriculumDay and VocabularyGroup tables for all 30 days.

Run: python -m app.seed.seed
"""

import asyncio
import uuid
import logging

from sqlalchemy import select

from app.database import engine, Base, async_session_factory
from app.models.curriculum import CurriculumDay
from app.models.vocabulary import VocabularyGroup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Seed package init ─────────────────────────────────────────────────────────

