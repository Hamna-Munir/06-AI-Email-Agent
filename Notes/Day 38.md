# Day 38 — Email Tools & Tool Calling

**Objective:** Teach the agent to use tools instead of only generating text.

---

## 📖 Theory

### Tool calling (recap from Week 5)

As established in Week 5, tool calling lets the LLM decide to invoke a specific function with specific arguments, rather than only producing text. For the email agent, this is what turns "understanding" an email (Day 36-37) into actually *doing* something about it.

### Function schemas, tool selection, arguments, execution, results

The same round-trip from Week 5 applies here:

```
LLM decides to call a tool → provides arguments → application executes the real function → result is returned to the LLM → LLM continues or produces a final response
```

### Agent loop (recap)

The agent keeps deciding → acting → observing until it has enough information to finish — for an email agent, this might mean searching for related emails, checking a calendar, then drafting a reply, all before producing a final response to the user.

### Tool errors

A tool can fail for reasons unrelated to the agent's reasoning — a search with no matches, a malformed argument, a missing email ID. These need to be handled gracefully (an error string back to the LLM, not a crash), exactly as established in Week 5.

### Example tools for this project

For this first version, these use mock/local data rather than a real inbox:

- `search_emails(query)` — find emails matching a query
- `get_email(email_id)` — retrieve one specific email by ID
- `create_draft(to, subject, body)` — create a draft reply (does not send)
- `search_contacts()` — look up a contact
- `get_calendar_availability()` — check available meeting times

---

## 💻 Coding Exercise

```python
def search_emails(query):
    ...

def get_email(email_id):
    ...

def create_draft(to, subject, body):
    ...
```

Then let the model select the appropriate tool based on the email's content — the code should not hardcode which tool gets called for which email type.

---

## 🛠 Mini Project — Tool-Using Email Agent

**Example:**

```
User:
Find my previous emails about the project meeting.

Agent:
Decision → search_emails()
Tool → results
Observation → relevant email found
Decision → summarize
```

---

## 🧠 Quiz

1. What is tool calling, in one sentence?
2. Who actually executes the tool — the LLM or your application code?
3. What is a tool schema?
4. Why should tool arguments be validated before executing the real function?

*(Try answering from memory first, then check the theory section above.)*

---

## ⭐ Bonus

Add a `delete_draft()` tool — but do **not** allow it to execute automatically (this connects directly to Day 40's human-in-the-loop safety work).

---

## 🐞 Common Errors

| Error | Likely Cause | Fix |
|---|---|---|
| Letting the LLM directly execute arbitrary code | Trusting model output as executable code instead of routing through defined tool functions | Only ever call pre-defined, explicitly scoped functions — never `eval()` or similar on model output |
| No argument validation | Passing tool-call arguments straight into the function without checking | Validate arguments (types, required fields) before executing, same as Week 5's tool error handling |
| Tool names that are ambiguous | Two tools with unclear, overlapping descriptions | Write specific, distinct descriptions so the model can reliably pick the right one |
| No handling when a tool fails | Assuming every tool call succeeds | Wrap execution in error handling and return a clear message the LLM can act on |

---

## ✅ Checklist

- [ ] 3 tools built (search_emails, get_email, create_draft)
- [ ] Tool schemas written
- [ ] Tool execution implemented
- [ ] Tool errors handled
- [ ] Agent can choose the correct tool for a given email
- [ ] Git commit made

---

## 📂 GitHub Push

```bash
git add .
git commit -m "Day 38: Added email tools and tool calling"
git push
```

---

## 📝 Journal

*Explain: What did the LLM decide, and what did Python actually execute?*

---

## 🧠 Skill Learned

Tool calling
