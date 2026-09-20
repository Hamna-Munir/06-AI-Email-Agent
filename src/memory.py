"""
memory.py
Day 39 — email thread storage and context retrieval. Uses mock
in-memory thread data for this week (real inbox integration is a
separate later phase, per the roadmap).
"""

from openai import OpenAI
from src.config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL

client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

# Mock thread data — includes the curriculum's specific test case:
# a client requesting Friday, then changing it to Monday.
MOCK_THREADS = {
    "thread_1": [
        {"from": "client@example.com", "body": "Can we meet Friday to discuss the proposal?"},
        {"from": "me@company.com", "body": "Friday works for me. What time?"},
        {"from": "client@example.com", "body": "Actually, let's do Monday instead — something came up."},
    ],
    "thread_2": [
        {"from": "client@example.com", "body": "Do you have the Q3 report ready?"},
    ],
}


def get_thread_context(thread_id: str) -> list[dict]:
    """
    Day 39 — returns the relevant messages for a thread, in
    chronological order (oldest first), so the agent sees the
    conversation unfold correctly rather than out of sequence.

    Args:
        thread_id: identifier for the email thread.

    Returns:
        A list of message dicts (empty list if the thread doesn't exist).
    """
    return MOCK_THREADS.get(thread_id, [])


def summarize_thread(thread_id: str) -> str:
    """
    Day 39 bonus — condenses a thread into a short summary, useful as
    compressed context for long threads instead of sending every message.
    """
    messages = get_thread_context(thread_id)
    if not messages:
        return "No prior thread history."

    thread_text = "\n".join(f"{m['from']}: {m['body']}" for m in messages)

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{
                "role": "user",
                "content": (
                    f"Summarize this email thread in 1-2 sentences, "
                    f"making sure to capture the MOST RECENT request if "
                    f"it changed from an earlier message:\n\n{thread_text}"
                ),
            }],
            temperature=0.2,
            max_tokens=150,
        )
        return response.choices[0].message.content or "Could not summarize thread."
    except Exception as e:
        return f"(Thread summary failed: {str(e)[:60]})"
