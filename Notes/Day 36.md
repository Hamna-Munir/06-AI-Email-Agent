# Day 36 — Email Agent Fundamentals

**Objective:** Understand what makes an Email Agent different from an email-writing chatbot.

---

## 📖 Theory

### What is an AI email agent?

An AI email agent doesn't just generate a reply to an email — it reads an incoming email, understands what it's actually asking for, decides what should happen next, and (when appropriate) acts on that decision using tools. A chatbot that writes email text is one small piece of this; the agent is the whole decision-making system around it.

### Chatbot vs agent

- **Chatbot** — receives a message, generates a response. One step, no decision-making about *what to do*, only about *what to say*.
- **Agent** — receives an email, decides what it means, decides what action (if any) is appropriate, and may take multiple steps (classify → search → draft → confirm) before finishing.

### Email understanding

Before any action can be decided, the agent needs to understand what the email is actually about — not just the literal words, but the underlying request or purpose.

### Intent detection

Intent detection means identifying the *purpose* behind an email — is it a meeting request, a question, a complaint, a newsletter? This is the first real decision point in the agent's pipeline.

### Classification

Classification assigns the email to a category (e.g., Meeting, Question, Request, Newsletter, Urgent, Other) based on its detected intent. This category then informs what the agent should do next — a newsletter needs no reply; a meeting request probably does.

### Agent decision loop

```
Observation → Decision → Action
```

The agent observes the email, decides what it means and what to do, and takes an action (which might itself produce a new observation, continuing the loop — this is the same fundamental agent loop from Week 5, now applied to email instead of research).

### Why email is a good agent use case

Email is naturally varied (meetings, questions, newsletters, urgent issues), requires understanding context (threads, prior messages), and has real consequences for wrong actions (sending something unintended) — making it a realistic testbed for intent detection, tool use, context management, and safety, all in one project.

---

## 🎥 Best Resource

Search YouTube for: "AI Agents Explained Tool Calling Function Calling" — pick one recent, technically focused explanation rather than a motivational overview.

---

## 💻 Coding Exercise

Create the project skeleton:

```
email_agent/
├── app.py
├── agent.py
├── email_parser.py
└── prompts.py
```

Sample emails to test with:

```python
emails = [
    {
        "from": "client@example.com",
        "subject": "Meeting request",
        "body": "Can we schedule a meeting tomorrow?"
    },
    {
        "from": "newsletter@example.com",
        "subject": "Weekly Newsletter",
        "body": "Here are this week's updates..."
    }
]
```

Build a basic email classifier that assigns one of: Meeting, Question, Request, Newsletter, Urgent, Other.

---

## 🛠 Mini Project — Email Intent Classifier

**Input:** an email (subject + body)
**Output:** intent + short reasoning for why that intent was chosen

---

## 🧠 Quiz

1. What makes an agent different from a normal LLM call?
2. Why classify an email before deciding what to do?
3. What is an email intent?
4. Give 3 possible email actions.

*(Try answering from memory first, then check the theory section above.)*

---

## ⭐ Bonus

Add a `priority` field: low / medium / high.

---

## 🐞 Common Errors

| Error | Likely Cause | Fix |
|---|---|---|
| Asking the model for unstructured output | No explicit format specified for the classification response | Request a specific category label, not free-form text (structured output is formalized on Day 37) |
| Mixing classification and reply generation | Trying to do both in one prompt/step | Keep classification as its own distinct step before any reply is drafted |
| No fallback category | Assuming every email will cleanly fit Meeting/Question/Request/Newsletter/Urgent | Always include an "Other" category so nothing is forced into the wrong bucket |
| Treating every email as requiring a reply | Not distinguishing informational emails (newsletters) from actionable ones | Let classification determine whether a reply is even needed, not assume "yes" by default |

---

## ✅ Checklist

- [ ] Email agents understood
- [ ] Email Intent Classifier built
- [ ] Tested against 10 sample emails
- [ ] Git commit made

---

## 📂 GitHub Push

```bash
git add .
git commit -m "Day 36: Email agent fundamentals + intent classifier"
git push
```

---

## 📝 Journal

*Write: What makes an email workflow agentic rather than just generative?*

---

## 🧠 Skill Learned

Email intent classification
