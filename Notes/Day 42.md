# Day 42 — Testing, Evaluation & Deployment

**Objective:** Don't finish with "it works on my example." Finish with evidence.

---

## 📖 Theory

### Why rigorous evaluation matters here specifically

This is the same evaluation discipline established in Week 2 (Day 13), Week 3 (Day 20), Week 4 (Day 27), and Week 5 (Day 34) — now applied to an agent with real-world consequences (sending, deleting) rather than just generating text. The stakes of an unverified failure are higher here: a wrong answer in a research report is a quality issue, but an agent that sends the wrong email or ignores a prompt injection is a safety issue.

### What to measure

- **Intent accuracy** — did classification (Day 36) correctly identify what the email was about?
- **Correct tool selection** — did the agent pick the right tool (Day 38) for the situation?
- **Correct arguments** — were the tool's arguments actually valid and appropriate?
- **Context accuracy** — did the agent correctly use thread history (Day 39), especially when requirements changed mid-thread?
- **Safety behavior** — did sensitive actions correctly require confirmation (Day 40), and did the agent correctly resist prompt injection?
- **Draft quality** — is the generated reply actually usable?
- **Failure handling** — did tool failures produce a graceful error instead of a crash?

---

## 🧪 Evaluation Dataset

At least **20 test emails**, covering:

- 5 normal emails
- 5 business emails
- 3 ambiguous emails
- 3 context-dependent emails
- 2 tool failures
- 2 malicious/prompt-injection emails

### Example evaluation table

| Test | Expected | Actual | Pass |
|---|---|---|---|
| Meeting request | Draft reply | Draft reply | ✅ |
| Newsletter | No reply | No reply | ✅ |
| Tool failure | Graceful error | Graceful error | ✅ |
| Malicious email | Reject instruction | Rejected | ✅ |

Fill this in with real results from actually running all 20+ test emails — not a theoretical prediction of what should happen.

---

## 🚀 Deployment

Deploy the demo version, keeping email data mocked/local for this first deployment — connecting real OAuth credentials would complicate deployment and isn't necessary to demonstrate the agent's actual reasoning, tools, and safety behavior (real integration is a deliberately separate phase, per this week's plan).

---

## 🧠 Quiz

1. Why is "it works on my example" not sufficient evidence that an agent is reliable?
2. Why does an agent with real-world side effects (send, delete) need more rigorous evaluation than one that only generates text?
3. What does "safety behavior" mean as an evaluation category, distinct from "draft quality"?
4. Why keep email data mocked for the first deployment instead of connecting a real inbox immediately?

*(Try answering from memory first, then check the theory section above.)*

---

## 🐞 Common Errors

| Error | Likely Cause | Fix |
|---|---|---|
| Only testing the easy/happy-path cases | Confirmation bias — running the cases most likely to succeed | Deliberately include ambiguous, tool-failure, and malicious cases in the 20-email set |
| Treating "no crash" as "passed" | Conflating reliability with correctness | Judge each test against its *expected* behavior, not just whether it ran without error |
| Skipping the prompt-injection tests | Assuming Day 40's fix "obviously" works | Actually run both malicious test emails and record the real outcome |
| Deploying with real OAuth too early | Wanting a "real" demo immediately | Confirm the mocked-data version is fully correct first — OAuth issues can mask whether the agent itself actually works |

---

## ✅ Checklist

- [ ] 20+ test emails created across all 6 categories
- [ ] Evaluation table filled in with real results
- [ ] Intent accuracy measured
- [ ] Correct tool selection measured
- [ ] Context accuracy measured (including the changed-requirements case)
- [ ] Safety behavior measured (both malicious emails tested)
- [ ] Failure handling measured
- [ ] Demo deployed (mocked data)
- [ ] Git commit made

---

## 📂 GitHub Push

```bash
git add .
git commit -m "Day 42: Full evaluation and deployment"
git push
```

---

## 🧠 Skill Learned

Agent evaluation + deployment
