"""
agent.py
Day 38 -> tool-calling agent loop for email actions.
Day 41 -> full integration: analysis -> decision -> tools -> activity log.
Day 40 -> sensitive actions (send/delete) are never in this loop's tool
           set at all — they're handled as a separate, explicit
           confirmation step outside the agent's own decision-making,
           so there's no code path where the agent could execute them
           without a human in the loop.
"""

import json
from datetime import datetime
from openai import OpenAI
from src.config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL
from src.tools import TOOL_SCHEMAS, execute_tool
from src.prompts import AGENT_SYSTEM_PROMPT
from src.email_parser import analyze_email
from src.memory import get_thread_context
from src.safety import flag_possible_injection

client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

MAX_ITERATIONS = 6  # Week 5 lesson: hard cap prevents an infinite agent loop


def process_email(email: dict) -> dict:
    """
    Day 41 — full pipeline for one incoming email: analyze -> decide ->
    act (via tools) -> log every step, with sensitive actions excluded
    from the loop entirely (they're proposed, not executed, here).

    Args:
        email: dict with 'from', 'subject', 'body', and optionally 'thread_id'.

    Returns:
        A dict with 'analysis', 'activity_log', 'agent_response',
        'injection_flagged', and 'tool_calls'.
    """
    activity_log = []

    def log(message: str):
        activity_log.append(f"{datetime.now().strftime('%H:%M:%S')} — {message}")

    log("Email received")

    # Day 40 — flag (not block) possible injection attempts for the
    # human reviewer; the real defense is the system prompt itself.
    injection_flagged = flag_possible_injection(email.get("body", ""))
    if injection_flagged:
        log("⚠️ Possible prompt injection detected in email body — flagged for review")

    # Day 37 — structured analysis
    analysis = analyze_email(
        subject=email.get("subject", ""),
        body=email.get("body", ""),
        sender=email.get("from", ""),
    )
    log(f"Classified as {analysis.intent} (priority: {analysis.priority})")

    # Day 39 — thread context, if this email belongs to a thread
    thread_context = []
    if email.get("thread_id"):
        thread_context = get_thread_context(email["thread_id"])
        if thread_context:
            log(f"Retrieved thread context ({len(thread_context)} prior messages)")

    # Day 36 — newsletters and similar don't need agent action
    if not analysis.needs_reply:
        log("No reply needed — no further action taken")
        return {
            "analysis": analysis,
            "activity_log": activity_log,
            "agent_response": "No action needed.",
            "injection_flagged": injection_flagged,
            "tool_calls": [],
        }

    # Day 38 — agent decision + tool-calling loop
    context_text = "\n".join(f"{m['from']}: {m['body']}" for m in thread_context)
    user_message = (
        f"Email from {email.get('from', 'unknown')}:\n"
        f"Subject: {email.get('subject', '')}\n"
        f"Body: {email.get('body', '')}\n\n"
        f"Analysis: intent={analysis.intent}, requested_action={analysis.requested_action}\n"
        f"{'Thread context: ' + context_text if context_text else ''}\n\n"
        f"Decide what to do (search, check calendar, draft a reply, etc.) "
        f"using the available tools."
    )

    messages = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    tool_call_log = []

    for _ in range(MAX_ITERATIONS):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.2,
            )
        except Exception as e:
            log(f"Agent call failed: {str(e)[:60]}")
            return {
                "analysis": analysis,
                "activity_log": activity_log,
                "agent_response": "Something went wrong processing this email. Please review manually.",
                "injection_flagged": injection_flagged,
                "tool_calls": tool_call_log,
            }

        message = response.choices[0].message

        if not message.tool_calls:
            log("Agent finished — response ready")
            return {
                "analysis": analysis,
                "activity_log": activity_log,
                "agent_response": message.content,
                "injection_flagged": injection_flagged,
                "tool_calls": tool_call_log,
            }

        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                arguments = {}

            log(f"Selected {tool_name}()")
            result = execute_tool(tool_name, arguments)
            log(f"{tool_name}() returned a result")
            tool_call_log.append({"tool": tool_name, "arguments": arguments, "result": result})

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

    log("Reached step limit before finishing")
    return {
        "analysis": analysis,
        "activity_log": activity_log,
        "agent_response": "The agent reached its step limit. Please review manually.",
        "injection_flagged": injection_flagged,
        "tool_calls": tool_call_log,
    }
