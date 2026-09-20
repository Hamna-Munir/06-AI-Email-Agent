"""
tools.py
Day 38 — email tools using mock/local data. Real inbox integration is
a deliberately separate later phase (per the roadmap), so the agent's
reasoning, tool selection, and safety behavior can be verified first.
"""

from src.memory import get_thread_context, summarize_thread

# ---------------------------------------------------------------------------
# Mock inbox data
# ---------------------------------------------------------------------------

MOCK_EMAILS = {
    "email_1": {"from": "client@example.com", "subject": "Meeting request", "body": "Can we schedule a meeting tomorrow?", "thread_id": None},
    "email_2": {"from": "newsletter@example.com", "subject": "Weekly Newsletter", "body": "Here are this week's updates...", "thread_id": None},
    "email_3": {"from": "client@example.com", "subject": "Re: Proposal", "body": "Actually, let's do Monday instead — something came up.", "thread_id": "thread_1"},
    "email_4": {"from": "boss@company.com", "subject": "URGENT: Server down", "body": "The production server is down, need this fixed ASAP.", "thread_id": None},
}

MOCK_CONTACTS = {
    "client@example.com": {"name": "Alex Chen", "company": "Acme Corp"},
    "boss@company.com": {"name": "Jordan Smith", "role": "Engineering Manager"},
}

MOCK_CALENDAR_SLOTS = ["Monday 10:00 AM", "Monday 2:00 PM", "Tuesday 11:00 AM"]

# Drafts created this session (in-memory only)
_drafts = []


# ---------------------------------------------------------------------------
# Tool functions
# ---------------------------------------------------------------------------

def search_emails(query: str) -> list[dict]:
    """Searches mock emails for a keyword match in subject or body."""
    query_lower = query.lower()
    results = [
        {"email_id": eid, **email}
        for eid, email in MOCK_EMAILS.items()
        if query_lower in email["subject"].lower() or query_lower in email["body"].lower()
    ]
    return results if results else []


def get_email(email_id: str):
    """Retrieves one email by ID."""
    email = MOCK_EMAILS.get(email_id)
    if not email:
        return f"Error: no email found with ID '{email_id}'."
    return email


def create_draft(to: str, subject: str, body: str) -> dict:
    """Creates a draft reply. This does NOT send anything — drafts are safe (Day 40)."""
    draft = {"to": to, "subject": subject, "body": body, "status": "draft"}
    _drafts.append(draft)
    return draft


def search_contacts(name_or_email: str):
    """Looks up a contact by name or email."""
    for email, info in MOCK_CONTACTS.items():
        if name_or_email.lower() in email.lower() or name_or_email.lower() in info["name"].lower():
            return {"email": email, **info}
    return f"No contact found matching '{name_or_email}'."


def get_calendar_availability() -> list[str]:
    """Returns mock available meeting slots."""
    return MOCK_CALENDAR_SLOTS


def delete_draft(draft_index: int):
    """
    Day 38 bonus — exists as a tool, but per Day 40's safety rules,
    it is NEVER allowed to execute automatically (see safety.py's
    SENSITIVE_ACTIONS — this should always be gated behind confirmation
    if it were ever exposed to the agent's automatic tool loop).
    """
    if 0 <= draft_index < len(_drafts):
        removed = _drafts.pop(draft_index)
        return {"deleted": removed}
    return "Error: no draft at that index."


# ---------------------------------------------------------------------------
# Tool registry + schemas
# ---------------------------------------------------------------------------

TOOL_FUNCTIONS = {
    "search_emails": search_emails,
    "get_email": get_email,
    "create_draft": create_draft,
    "search_contacts": search_contacts,
    "get_calendar_availability": get_calendar_availability,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_emails",
            "description": "Searches the inbox for emails matching a keyword in subject or body.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_email",
            "description": "Retrieves a specific email by its ID.",
            "parameters": {
                "type": "object",
                "properties": {"email_id": {"type": "string"}},
                "required": ["email_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_draft",
            "description": "Creates a draft reply. Does not send it — drafts are safe and never require confirmation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_contacts",
            "description": "Looks up a contact by name or email address.",
            "parameters": {
                "type": "object",
                "properties": {"name_or_email": {"type": "string"}},
                "required": ["name_or_email"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_calendar_availability",
            "description": "Returns a list of available meeting time slots.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def execute_tool(tool_name: str, arguments: dict):
    """Safely executes a tool by name — never raises, always returns a result or error string."""
    if tool_name not in TOOL_FUNCTIONS:
        return f"Error: unknown tool '{tool_name}'."
    try:
        return TOOL_FUNCTIONS[tool_name](**arguments)
    except Exception as e:
        return f"Error executing '{tool_name}': {str(e)}"
