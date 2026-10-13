"""
AI Coach Service — wrapper around the Anthropic (Claude) API.

Provides two strictly separated modes:
  1. CORRECTION mode  — writing corrections, vocab checking, speaking practice
  2. INTERVIEW mode   — mock interview (no corrections mid-conversation)
"""

import json
import logging
from typing import Optional
from anthropic import AsyncAnthropic

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_client: Optional[AsyncAnthropic] = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


# ── System Prompts ────────────────────────────────────────────────────────────

CORRECTION_SYSTEM_PROMPT = """You are SpeakReady Coach — a supportive but honest English-communication coach for non-native speakers preparing for technical job interviews.

Your role:
- Help users speak and write clearly, naturally, and confidently.
- Prioritize clear, natural expression over textbook-perfect grammar.
- Use simple sentence patterns; avoid overly academic or complex language in your corrections.

When correcting writing:
- Break the user's text into individual sentences or error clusters.
- For EACH sentence/cluster, provide exactly four parts:
  1. "original" — their exact words
  2. "corrected" — grammatically correct version
  3. "natural" — a more natural, fluent rephrasing a native speaker might use
  4. "reason" — a one-line explanation of what was fixed (brief, no lectures)
- Return your response as valid JSON: {"blocks": [{"original": "...", "corrected": "...", "natural": "...", "reason": "..."}]}
- If a sentence is already perfect, still include it with corrected = original, natural = original, and reason = "No changes needed."

When in speaking/chat mode:
- Be conversational, warm, and encouraging.
- Gently correct errors inline while keeping the conversation flowing.
- Adapt to the day's topic and mode (self-intro, unprepared description, interview Q&A, free chat).

When checking vocabulary usage:
- Determine if the user used the target word/phrase naturally and correctly in context.
- Return JSON: {"is_correct": true/false, "feedback": "brief explanation"}

Never fabricate a pronunciation or confidence score from text-only input.
"""

INTERVIEW_SYSTEM_PROMPT = """You are SpeakReady Interviewer — a professional technical/HR interviewer conducting a mock interview.

Rules:
- Ask ONE question at a time. Wait for the user's full response before moving on.
- Do NOT correct grammar, vocabulary, or sentence structure during the interview.
- Do NOT coach or give hints during the interview.
- Keep your tone professional but not intimidating.
- Mix HR questions (tell me about yourself, strengths/weaknesses, why this role) with technical questions appropriate for an entry-level AI/ML/Data Analyst role.
- For a full mock interview, ask 6-8 questions total.
- When you've asked all questions, say exactly: "[INTERVIEW_COMPLETE]"

After the interview, when asked to score:
- Evaluate the FULL transcript across these 7 dimensions (each scored 1-10):
  1. grammar — accuracy of sentence structure
  2. vocabulary — range and appropriateness of word choice
  3. fluency — smoothness and coherence of responses
  4. pronunciation — set to null, add note "voice mode required"
  5. confidence — set to null, add note "voice mode required"
  6. structure — organization and completeness of answers (STAR method, etc.)
  7. overall — holistic communication effectiveness

- Return valid JSON:
{
  "grammar": <int>,
  "vocabulary": <int>,
  "fluency": <int>,
  "pronunciation": null,
  "confidence": null,
  "structure": <int>,
  "overall": <int>,
  "pronunciation_note": "voice mode required",
  "confidence_note": "voice mode required",
  "feedback": "<2-3 paragraphs of constructive, specific feedback>"
}
"""


# ── Correction Mode ──────────────────────────────────────────────────────────

async def correct_writing(user_text: str, writing_prompt: str) -> dict:
    """Send user's writing to Claude for structured 4-part correction."""
    client = _get_client()

    user_message = (
        f"The writing prompt was: \"{writing_prompt}\"\n\n"
        f"Here is the user's response:\n\n{user_text}\n\n"
        "Please analyze and correct this writing. Return your response as a JSON object "
        "with a 'blocks' array where each block has 'original', 'corrected', 'natural', and 'reason' fields."
    )

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=CORRECTION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        text = response.content[0].text

        # Try to extract JSON from response
        try:
            # Handle case where Claude wraps JSON in markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            result = json.loads(text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse correction JSON: {text[:200]}")
            result = {
                "blocks": [{
                    "original": user_text,
                    "corrected": user_text,
                    "natural": user_text,
                    "reason": "AI response could not be parsed. Please retry."
                }]
            }

        return result

    except Exception as e:
        logger.error(f"Claude API error in correct_writing: {e}")
        raise


async def check_vocab_mastery(
    user_sentence: str, headword: str, phrases: list[str]
) -> dict:
    """Check if the user used the vocab group correctly and naturally."""
    client = _get_client()

    user_message = (
        f"The target vocabulary group is:\n"
        f"- Headword: {headword}\n"
        f"- Related phrases: {', '.join(phrases)}\n\n"
        f"The user wrote: \"{user_sentence}\"\n\n"
        "Did they use the target word/phrase naturally and correctly? "
        "Return JSON: {\"is_correct\": true/false, \"feedback\": \"brief explanation\"}"
    )

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=CORRECTION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        text = response.content[0].text
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except json.JSONDecodeError:
            return {"is_correct": False, "feedback": "Could not evaluate. Please try again."}

    except Exception as e:
        logger.error(f"Claude API error in check_vocab_mastery: {e}")
        raise


async def speaking_chat(
    messages: list[dict], day_topic: str, mode: str
) -> str:
    """Generate next coach reply in a speaking practice conversation."""
    client = _get_client()

    system = (
        f"{CORRECTION_SYSTEM_PROMPT}\n\n"
        f"Current session context:\n"
        f"- Today's topic: {day_topic}\n"
        f"- Mode: {mode}\n"
        f"Keep responses concise (2-4 sentences). Be conversational."
    )

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system,
            messages=messages,
        )
        return response.content[0].text

    except Exception as e:
        logger.error(f"Claude API error in speaking_chat: {e}")
        raise


# ── Interview Mode ───────────────────────────────────────────────────────────

async def interview_ask(
    transcript: list[dict], interview_type: str, day_number: int
) -> str:
    """Generate the next interview question (or [INTERVIEW_COMPLETE])."""
    client = _get_client()

    context_note = ""
    if interview_type == "baseline":
        context_note = "This is the user's BASELINE interview (Day 0). Ask standard HR + technical questions to establish a starting point."
    elif interview_type == "final":
        context_note = "This is the user's FINAL interview (Day 30). Make it slightly more challenging to test their growth."

    system = f"{INTERVIEW_SYSTEM_PROMPT}\n\n{context_note}"

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=system,
            messages=transcript if transcript else [
                {"role": "user", "content": "I'm ready to start the mock interview."}
            ],
        )
        return response.content[0].text

    except Exception as e:
        logger.error(f"Claude API error in interview_ask: {e}")
        raise


async def interview_score(transcript: list[dict]) -> dict:
    """Score a completed mock interview across 7 dimensions."""
    client = _get_client()

    scoring_prompt = (
        "The mock interview is now complete. Here is the full transcript of questions and answers.\n\n"
        "Please score the candidate across all 7 dimensions and provide detailed feedback.\n"
        "Return your response as valid JSON with the scoring format specified in your instructions."
    )

    messages = transcript + [{"role": "user", "content": scoring_prompt}]

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=INTERVIEW_SYSTEM_PROMPT,
            messages=messages,
        )

        text = response.content[0].text
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse scoring JSON: {text[:200]}")
            return {
                "grammar": None, "vocabulary": None, "fluency": None,
                "pronunciation": None, "confidence": None,
                "structure": None, "overall": None,
                "pronunciation_note": "voice mode required",
                "confidence_note": "voice mode required",
                "feedback": "Scoring could not be parsed. Please retry."
            }

    except Exception as e:
        logger.error(f"Claude API error in interview_score: {e}")
        raise

