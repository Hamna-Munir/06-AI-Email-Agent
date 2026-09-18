# Day 37 — Structured Email Understanding

**Objective:** Make the agent convert messy email text into structured information.

---

## 📖 Theory

### Structured output (recap + deeper look)

As introduced in earlier weeks, structured output means getting the model to return data in a predictable, machine-readable shape (like JSON) instead of free-form text. For an email agent, this is what turns "the model read the email" into "the code can actually act on what the model understood."

### JSON schemas

A JSON schema defines exactly what fields a structured response must contain and what type each field should be. This is the contract between the LLM's output and the rest of the application — without it, the code has no guarantee the response will be usable.

### Pydantic

**Pydantic** is a Python library for defining data models with type validation built in. Instead of manually checking that a dictionary has the right keys and types, a Pydantic model does this automatically and raises a clear error if the data doesn't match — making it a natural fit for validating LLM output before trusting it.

### Entity extraction

Entity extraction means pulling out specific, named pieces of information from text — a date, a person's name, a deadline — rather than just understanding the email's general topic.

### Intent + urgency + requested action

Beyond just classifying an email's category (Day 36), a fuller understanding includes: how urgent it is, and what specific action the sender is actually asking for (e.g., "schedule a meeting" vs. just "read for information").

### Why structured data matters for agents

An agent that only has "the email is about a meeting" (unstructured understanding) can't reliably decide what to do next. An agent with `{"intent": "meeting_request", "requested_action": "schedule meeting", "needs_reply": true}` has exactly what it needs to make a concrete decision — this is what makes structured output foundational for the tool-calling and decision-making steps that come later this week.

---

## 💻 Coding Exercise

Define the target structure:

```json
{
  "intent": "meeting_request",
  "priority": "high",
  "sender": "client@example.com",
  "requested_action": "schedule meeting",
  "needs_reply": true,
  "summary": "Client wants to schedule a meeting."
}
```

Build an `EmailAnalysis` Pydantic model with fields:

```python
from pydantic import BaseModel

class EmailAnalysis(BaseModel):
    intent: str
    priority: str
    summary: str
    requested_action: str
    needs_reply: bool
```

---

## 🛠 Mini Project — Email Analyzer

**Input:** Subject + Body
**Output:** Intent, Priority, Summary, Requested Action, Reply Required — all as validated structured data, not free text.

---

## 🧠 Quiz

1. Why use structured output instead of letting the model respond freely?
2. Why is Pydantic useful here specifically?
3. What should happen if the model returns invalid JSON?
4. What's the difference between a summary and a requested action?

*(Try answering from memory first, then check the theory section above.)*

---

## ⭐ Bonus

Add two more fields: `deadline` and `people_mentioned`.

---

## 🐞 Common Errors

| Error | Likely Cause | Fix |
|---|---|---|
| Assuming JSON will always be valid | Trusting LLM output without validation | Always validate through the Pydantic model and handle the exception when it fails |
| No validation | Parsing the raw model response directly without a schema check | Route every response through the Pydantic model before using it anywhere else |
| Too many unnecessary fields | Adding fields "just in case" that the agent never actually uses | Keep the schema to what's actually needed for downstream decisions |
| Confusing sentiment with intent | Treating "the sender sounds annoyed" as the same as "what they're asking for" | Keep these conceptually separate — intent is about the request, not the tone |

---

## ✅ Checklist

- [ ] Pydantic schema (`EmailAnalysis`) built
- [ ] Structured LLM output implemented
- [ ] Validation in place
- [ ] Error fallback for invalid output
- [ ] Tested against 10 emails
- [ ] Git commit made

---

## 📂 GitHub Push

```bash
git add .
git commit -m "Day 37: Structured email understanding"
git push
```

---

## 📝 Journal

*Document one case where structured output made the agent easier to control.*

---

## 🧠 Skill Learned

Structured output + information extraction
