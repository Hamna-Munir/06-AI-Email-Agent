# Day 39 — Context & Email Threads

**Objective:** Make the agent understand conversation context, not just the single latest email.

---

## 📖 Theory

### Email threads

An email thread is a sequence of back-and-forth messages on the same topic. Understanding a thread means understanding how the conversation evolved — not just reading the most recent message in isolation.

### Conversation history

Conversation history is the record of everything said so far in a thread. For an agent to reply sensibly, it often needs to know what was already discussed, agreed, or changed earlier in the exchange.

### Context windows (recap)

As covered in Week 3 (Day 18), every model has a limited context window. A long email thread can't always be sent in full — the same chunking/selection principles from document AI apply here too.

### Short-term memory

Short-term memory, in this context, means the agent's ability to "remember" earlier messages in the current thread for the duration of handling it — not a permanent memory across all future conversations, just enough to reply coherently within this one exchange.

### Relevant context retrieval

Rather than blindly including every message in a thread, relevant context retrieval means selecting the messages that actually matter for producing the current reply — similar in spirit to Week 4's semantic retrieval, but applied to conversation history instead of documents.

### Context compression

When a thread is long, context compression means summarizing older parts of the conversation instead of including them verbatim, so the most relevant recent context isn't crowded out by less important earlier messages.

### Why blindly sending the entire thread is bad

```
Email 1
↓
Email 2
↓
Email 3
↓
Current email
```

If the agent just concatenates every message and sends it all to the LLM, it risks: exceeding the context window, diluting relevant information with outdated details, and — critically — missing that something changed partway through the thread (e.g., a rescheduled meeting time). The agent should understand the previous conversation before drafting a reply, not just react to the newest message alone.

---

## 💻 Coding Exercise

```python
def get_thread_context(thread_id):
    # Return only the relevant messages, not necessarily the entire thread
    ...
```

---

## 🛠 Mini Project — Context-Aware Email Reply Agent

**Input:** previous thread + new email
**Output:** understanding of the conversation + a suggested reply that reflects it

**Test case:**

> Client previously requested Friday, then changed it to Monday.

The agent should reply based on the **latest** context (Monday), not the first message (Friday) — this is the concrete test that proves context is actually being used correctly, not just present.

---

## 🧠 Quiz

1. What is short-term memory, in this context?
2. Why can *more* context sometimes make an agent's response worse, not better?
3. Why should email threads be processed in chronological order?
4. When a thread contains conflicting requests over time, which information should be prioritized?

*(Try answering from memory first, then check the theory section above.)*

---

## ⭐ Bonus

Add a `summarize_thread()` function that condenses a long thread into a short summary usable as compressed context.

---

## 🐞 Common Errors

| Error | Likely Cause | Fix |
|---|---|---|
| Using only the latest email | Ignoring thread history entirely | Explicitly retrieve and pass relevant prior context, not just the newest message |
| Sending huge unnecessary context | Including the entire thread regardless of length | Apply relevant context retrieval / compression instead of dumping everything |
| Losing chronological order | Messages processed or displayed out of sequence | Sort thread messages by timestamp before using them |
| Forgetting the latest user intent | Treating an early message as still authoritative after it's been superseded | Weight the most recent relevant message higher when there's a conflict (the Friday→Monday test case) |

---

## ✅ Checklist

- [ ] Thread storage implemented
- [ ] Context retrieval implemented (`get_thread_context`)
- [ ] Thread summarization added
- [ ] Context-aware reply working
- [ ] Tested the "changed requirements" scenario (Friday → Monday)
- [ ] Git commit made

---

## 📂 GitHub Push

```bash
git add .
git commit -m "Day 39: Added email thread context"
git push
```

---

## 📝 Journal

*Record one example where context changed the correct response.*

---

## 🧠 Skill Learned

Context management / short-term memory
