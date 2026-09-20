"""
email_parser.py
Day 36 -> classify_email(): basic intent classification.
Day 37 -> EmailAnalysis (Pydantic) + analyze_email(): structured
           understanding of an email (intent, priority, summary,
           requested action, whether a reply is needed).
"""

import json
from typing import Optional
from pydantic import BaseModel, ValidationError
from openai import OpenAI
from src.config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL

client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

VALID_INTENTS = ["meeting", "question", "request", "newsletter", "urgent", "other"]


# ---------------------------------------------------------------------------
# Day 37 — Structured output schema
# ---------------------------------------------------------------------------

class EmailAnalysis(BaseModel):
    intent: str
    priority: str  # low / medium / high
    summary: str
    requested_action: str
    needs_reply: bool
    deadline: Optional[str] = None
    people_mentioned: Optional[list[str]] = None


def analyze_email(subject: str, body: str, sender: str = "") -> EmailAnalysis:
    """
    Day 37 — converts an email into structured, validated data instead
    of free text. Falls back to a safe default EmailAnalysis if the
    model's response is invalid or the call fails, rather than crashing.

    Args:
        subject: email subject line.
        body: email body text. Treated strictly as data to analyze,
              never as instructions (see prompts.py's system prompt).
        sender: sender's email address, if known.

    Returns:
        A validated EmailAnalysis instance.
    """
    from src.prompts import EMAIL_ANALYSIS_SYSTEM_PROMPT

    user_prompt = (
        f"Sender: {sender}\n"
        f"Subject: {subject}\n"
        f"Body:\n{body}\n\n"
        f"Return ONLY a JSON object with these exact fields: "
        f"intent (one of {VALID_INTENTS}), priority (low/medium/high), "
        f"summary (one sentence), requested_action (short phrase), "
        f"needs_reply (true/false), deadline (string or null), "
        f"people_mentioned (list of strings or null)."
    )

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": EMAIL_ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=400,
        )
        raw = response.choices[0].message.content or ""
        raw = raw.strip().strip("```json").strip("```").strip()
        data = json.loads(raw)
        return EmailAnalysis(**data)

    except (json.JSONDecodeError, ValidationError, Exception) as e:
        # Reliability fix (same pattern as Week 5): never crash — return
        # a safe, honest default that flags the analysis failure.
        return EmailAnalysis(
            intent="other",
            priority="medium",
            summary=f"(Analysis failed: {str(e)[:80]}) Subject: {subject}",
            requested_action="Manual review needed",
            needs_reply=True,
        )


# ---------------------------------------------------------------------------
# Day 36 — Basic intent classifier (kept separate/simple, EmailAnalysis
# above is the fuller Day 37 version used by the actual agent)
# ---------------------------------------------------------------------------

def classify_email(subject: str, body: str) -> dict:
    """
    Day 36 — a simple standalone classifier returning intent + reasoning,
    kept as the basic building block before Day 37's fuller structured version.
    """
    analysis = analyze_email(subject, body)
    return {"intent": analysis.intent, "reasoning": analysis.summary}
