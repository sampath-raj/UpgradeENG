# SpeakReady — Implementation Plan

A production-ready English communication and interview-readiness coach for engineering students.

## Overview

SpeakReady is a 30-day, milestone-based English-speaking coach built as a full-stack web app. Users work through structured daily modules, get AI-generated correction/feedback via Claude, and track progress toward a Day-1 vs Day-30 final comparison.

---

## User Review Required

> [!IMPORTANT]
> **Anthropic API Key required.** The MVP uses Claude (Anthropic) for all AI features. You'll need to supply the key in a `.env` file. The plan will include a placeholder — just paste your key before running.

> [!IMPORTANT]
> **No real deployment configured.** The plan targets Docker Compose for local dev only. Azure deploy scripts are out of scope for MVP but the Dockerfiles will be Azure-ready.

> [!WARNING]
> **Phase 2 (voice/audio) is explicitly NOT built.** Pronunciation + Confidence scoring will display as "voice mode required" in mock interview results.

---

## Open Questions

> [!IMPORTANT]
> **Auth style:** The spec says "email/password or magic link." I'll implement **email + password with JWT** (simpler, no email provider needed for local dev). Should I add OAuth (Google) too?

> [!IMPORTANT]
> **Seeded content:** Day-by-day prompts/grammar topics are not provided verbatim — I'll generate realistic, high-quality curriculum content for all 30 days inline as seed SQL. Do you want to review the content before the seed runs, or should I proceed and let you edit it later?

> [!NOTE]
> **Database location:** PostgreSQL runs in Docker Compose. No cloud DB is configured for MVP. This can be swapped for Azure Database for PostgreSQL later without code changes.

---

## Proposed Changes

### Milestone 1 — Repo Scaffold & Docker Compose

#### [NEW] `docker-compose.yml`
Full-stack orchestration: `postgres`, `backend` (FastAPI), `frontend` (React + Vite), and `pgadmin` (optional dev convenience).

#### [NEW] `backend/` — FastAPI app
```
backend/
  app/
    main.py          # FastAPI entrypoint, CORS, routers
    config.py        # Settings (env vars, Anthropic key, DB URL)
    database.py      # SQLAlchemy async engine + session
    models/          # SQLAlchemy ORM models
      user.py
      curriculum.py
      vocabulary.py
      writing.py
      speaking.py
      mock_interview.py
      progress.py
    schemas/         # Pydantic v2 request/response schemas
    routers/
      auth.py        # signup, login, me
      curriculum.py  # days, unlock logic
      writing.py     # submit, get corrections
      vocabulary.py  # groups, practice, mastered
      speaking.py    # chat session
      mock_interview.py
      progress.py
    services/
      ai_coach.py    # Claude API wrapper — correction mode + interview mode as SEPARATE functions
      spaced_rep.py  # Vocab spaced-repetition logic
    seed/
      seed.py        # Populates CurriculumDay + VocabularyGroup for all 30 days
  Dockerfile
  requirements.txt
  alembic/          # DB migrations
```

#### [NEW] `frontend/` — React + Vite + Tailwind
```
frontend/
  src/
    main.jsx
    App.jsx
    api/            # Axios client + endpoint wrappers
    components/
      Layout/
      Auth/
      Dashboard/
      DayModule/
      Writing/
      Vocabulary/
      Speaking/
      MockInterview/
      Progress/
    pages/
      Login.jsx
      Signup.jsx
      Onboarding.jsx
      Dashboard.jsx
      DayPage.jsx
      WritingPage.jsx
      VocabPage.jsx
      SpeakingPage.jsx
      MockInterviewPage.jsx
      ProgressPage.jsx
      ComparisonPage.jsx   # Day 1 vs Day 30
    hooks/
      useAuth.js
      useDay.js
      useProgress.js
    context/
      AuthContext.jsx
  Dockerfile
  vite.config.js
  tailwind.config.js
  postcss.config.js
```

---

### Milestone 2 — Curriculum Seed Data (all 30 days)

#### [NEW] `backend/app/seed/seed.py`

Populates:
- `CurriculumDay` — 30 rows with: day_number, week (1–4), focus_topic, grammar_topic, speaking_prompt, writing_prompt, is_milestone_day
- `VocabularyGroup` — 10–15 groups per day, each with headword + related phrases (e.g. "enhance", "enhance my skills", "enhance performance")

**Week themes:**
| Week | Days | Theme |
|------|------|-------|
| 1 | 1–7 | Foundation — Introductions, Self-presentation |
| 2 | 8–14 | Thinking in English — Descriptions, Opinions |
| 3 | 15–21 | Interview English — Answering, Storytelling |
| 4 | 22–30 | Pressure Training — Mock prep, Fluency drills |

---

### Milestone 3 — Writing Correction (end-to-end)

**Backend endpoint:** `POST /writing/submit`
- Saves submission immediately (no AI needed to store it)
- Calls `ai_coach.correct_writing(text, prompt_context)` → returns structured JSON
- Response schema:
```json
{
  "blocks": [
    {
      "original": "...",
      "corrected": "...",
      "natural": "...",
      "reason": "..."
    }
  ]
}
```
- If Claude call fails → saves submission with `correction_json = null`, queues a background retry task (FastAPI BackgroundTasks)

**Frontend:** Writing submission form → loading state → rendered correction blocks, styled card-per-block.

---

### Milestone 4 — Vocabulary Builder

**Backend:** 
- `GET /vocab/day/{day}` — returns groups for the day
- `POST /vocab/practice` — log a user sentence against a group (status = `practiced`)
- `POST /vocab/check-mastered` — sends user's sentence to Claude with a lightweight "did they use it naturally?" check; if yes, promote to `mastered`
- Spaced repetition: surface groups older than 3 days where status ≠ `mastered` into review queue

**Frontend:** 
- Card per vocab group (headword + phrases + examples)
- Input field for user sentence
- Status badge: `not started` → `practiced` → `mastered`

---

### Milestone 5 — Speaking Practice (text mode)

**Backend:** `POST /speaking/chat`
- Body: `{ day_number, mode, messages: [{role, content}] }`
- System prompt: coach persona (correction mode) — distinct from interview persona
- Returns next coach message
- Saves full transcript to `SpeakingSession` on `POST /speaking/end`

**Frontend:** Chat UI with message bubbles. Day-specific mode selector (intro / unprepared description / interview Q&A / free chat).

---

### Milestone 6 — Mock Interview + Scoring

**Backend:**
- `POST /mock-interview/start` — creates session, returns first question
- `POST /mock-interview/respond` — sends user answer, returns next question (NO corrections mid-interview)
- `POST /mock-interview/finish` — sends full transcript to Claude in interviewer-mode prompt → returns 7-dimension scores JSON
- Score schema:
```json
{
  "grammar": 7,
  "vocabulary": 6,
  "fluency": 7,
  "pronunciation": null,
  "confidence": null,
  "structure": 8,
  "overall": 7,
  "pronunciation_note": "voice mode required",
  "confidence_note": "voice mode required",
  "feedback": "..."
}
```
- Checkpoint guard: Days 7/14/21/28 unlock mock interview. Day 30 = final interview.

**Frontend:** Full-screen interview UI (no corrections visible), debrief screen with radar chart of scores.

---

### Milestone 7 — Progress Dashboard

**Backend:**
- `GET /progress/summary` — streak, days completed, avg scores per dimension
- `GET /progress/trend` — scores over time (one point per mock interview)
- `GET /progress/comparison` — Day 0 baseline vs Day 30 final (transcript + scores side-by-side)

**Frontend:**
- Streak counter + calendar heatmap
- Line chart (per-dimension score over time) — recharts
- Vocab mastery count
- Writing submissions timeline
- Day-1 vs Day-30 comparison panel (milestone 6 prerequisite)

---

### Milestone 8 — Polish

- Mobile-first responsive breakpoints (Tailwind `sm:` / `md:`)
- Error toast system (AI failure → "Feedback queued, try refreshing in a minute")
- Loading skeletons
- Streak update on day completion
- "Practice any day" free mode (bypass sequential lock)

---

## Data Model (ORM)

```
User            id, name, email, password_hash, current_day, streak_count, created_at
CurriculumDay   day_number(PK), week_number, week_theme, focus_topic, grammar_topic,
                grammar_lesson_md, speaking_prompt, writing_prompt, is_milestone_day
VocabularyGroup id, day_number(FK), headword, phrases(JSON), example_sentences(JSON)
VocabPracticeEntry id, user_id(FK), group_id(FK), user_sentence, status, created_at
WritingSubmission  id, user_id, day_number, original_text, correction_json, created_at
SpeakingSession    id, user_id, day_number, mode, transcript_json, created_at
MockInterview      id, user_id, day_number, interview_type, transcript_json, scores_json, created_at
UserDayProgress    id, user_id, day_number, modules_completed(JSON), completed_at
```

---

## AI Prompt Architecture

Two strictly separate server-side system prompts:

| Mode | Endpoint | Behavior |
|------|----------|----------|
| **Correction** | `/writing/submit`, `/speaking/chat`, `/vocab/check-mastered` | Shows original → corrected → natural → reason. Conversational, supportive. |
| **Interview** | `/mock-interview/*` | Interviewer only. One question at a time. No correction until debrief. |

Both prompts pass the full user transcript per-request (stateless).

---

## Verification Plan

### Automated Tests
```bash
cd backend && pytest tests/ -v
```
- Auth: signup, login, JWT refresh
- Writing: submit + correction structure validation
- Mock interview: 7-score schema validation, null pronunciation/confidence

### Manual Verification
1. Sign up → complete onboarding (Day 0 baseline interview)
2. Complete Day 1 → writing submission renders 4-part correction blocks
3. Vocab group → practice → check mastered
4. Day 7 → mock interview → debrief shows scores, pronunciation = "voice mode required"
5. Dashboard shows streak + score trends
6. Day 30 comparison panel shows Day 0 vs Day 30 side by side

---

## Build Order (milestones)

- [x] M1: Scaffold (repo, Docker Compose, FastAPI, React, auth)
- [x] M2: Seed all 30 curriculum days + vocab groups
- [x] M3: Writing correction E2E
- [x] M4: Vocabulary builder
- [x] M5: Speaking practice (text)
- [x] M6: Mock interview + scoring
- [x] M7: Progress dashboard + comparison view
- [x] M8: Polish + mobile
