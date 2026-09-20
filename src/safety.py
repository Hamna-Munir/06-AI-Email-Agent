"""
safety.py
Day 40 — human-in-the-loop safety: which actions require confirmation,
and defense against prompt injection via email content.
"""

# Actions the agent may take, and which require explicit human
# confirmation before executing. "Never" actions aren't tools at all —
# they're simply not exposed to the agent (see tools.py).
SENSITIVE_ACTIONS = {"send_email", "delete_email"}
SAFE_ACTIONS = {"search_emails", "get_email", "create_draft", "search_contacts", "get_calendar_availability"}


def requires_confirmation(action: str) -> bool:
    """
    Day 40 — the core safety gate. Read/draft actions execute
    automatically; sending or deleting requires explicit human approval.

    Args:
        action: the tool/action name.

    Returns:
        True if this action must be confirmed by a human before executing.
    """
    return action in SENSITIVE_ACTIONS


# ---------------------------------------------------------------------------
# Prompt injection defense
# ---------------------------------------------------------------------------

# Common phrasings used in prompt-injection attempts. This is a
# lightweight, imperfect heuristic flag for the UI (shown as a warning
# to the human reviewer) — the REAL defense is architectural: the
# system prompt (see prompts.py) never lets the model treat email body
# text as instructions in the first place, regardless of what it says.
INJECTION_SIGNAL_PHRASES = [
    "ignore your previous instructions",
    "ignore all previous instructions",
    "disregard your instructions",
    "you are now",
    "new instructions:",
    "system:",
    "act as",
]


def flag_possible_injection(email_body: str) -> bool:
    """
    Best-effort heuristic flag for human reviewers — NOT the actual
    defense mechanism. Even if this misses a novel phrasing, the
    agent's system prompt is architected so email content is never
    treated as an instruction regardless of what it contains.

    Args:
        email_body: the raw email body text.

    Returns:
        True if the email body contains a common injection-attempt phrase.
    """
    text = email_body.lower()
    return any(phrase in text for phrase in INJECTION_SIGNAL_PHRASES)
