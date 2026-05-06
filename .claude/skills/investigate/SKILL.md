---
name: investigate
version: 1.0.0
description: "Systematic debugger. Root cause before any fix. Iron Law: no fixes without investigation. Hypothesis-driven ??form 3-5 hypotheses, test them cheaply before touching code. Stop after 3 failed fix attempts and escalate. Use when stuck on a bug."
allowed-tools:
  - Bash
  - Read
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
---

## Preamble (run first)

```bash
_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
echo "BRANCH: $_BRANCH"
# Auto-activate freeze to prevent accidental changes during investigation
_FREEZE=$(cat ~/.mystack/freeze.txt 2>/dev/null || echo "none")
if [ "$_FREEZE" = "none" ]; then
  echo "." > ~/.mystack/freeze.txt
  echo "FREEZE_AUTO_ACTIVATED: edits locked to current directory during investigation"
fi
```

Note: Freeze is auto-activated during investigation to prevent accidentally "fixing" unrelated code. Run `/stacksmith-safety off` after investigation to remove.

---

## Iron Law

**No fix without understanding the root cause.**

If you have attempted 3 different fixes and none worked: **STOP and escalate.** Do not guess a 4th fix. More attempts without new information just waste time and may make the system harder to understand.

---

## Step 1 ??Understand the symptom

Ask if not clearly provided:
- **Exact symptom** ??error message verbatim, wrong output, crash, silent failure?
- **Reproduction** ??always, sometimes (what triggers it), or intermittent?
- **When did it start** ??after what change? Or has it always been this way?
- **Environment** ??local, staging, prod? All three?
- **What was tried** ??what has already been attempted?

---

## Step 2 ??Form hypotheses

Based on the symptom, list **3?? possible root causes** ranked by likelihood. For each, state the evidence that points to it:

```
H1 (most likely, ~60%): [hypothesis]
  Evidence: [why you think this]
  Rules out: [what would disprove it]

H2 (~25%): [hypothesis]
  Evidence: [why you think this]
  Rules out: [what would disprove it]

H3 (~10%): [hypothesis]
  Evidence: [why you think this]

H4 (~5%): [hypothesis]
```

**Common hypothesis categories:**
- Wrong assumption about data (nil where non-nil expected, wrong type, wrong shape)
- State/timing issue (race condition, stale cache, wrong ordering)
- Config/environment mismatch (works local, fails staging)
- External dependency changed (API, library version)
- Regression from recent change (`git log --oneline -10`)

---

## Step 3 ??Test hypotheses cheaply (observe before touching code)

For each hypothesis, design a minimal test that confirms or rules it out ??**without modifying code**:

| Hypothesis | Test method | Cost |
|------------|-------------|------|
| H1: value is nil | Add `puts/console.log/print` at boundary | Trivial |
| H2: race condition | Log timestamps of competing operations | Trivial |
| H3: config issue | Print ENV values at startup | Trivial |
| H4: library bug | Pin version and reproduce | Low |

Run the cheapest tests first. Report results. Eliminate hypotheses.

```bash
# Check recent changes that might be relevant
git log --oneline -15
git log --since="7 days ago" --name-only --format="" | sort | uniq -c | sort -rn | head -10
```

---

## Step 4 ??Trace the data flow

Once narrowed to 1?? hypotheses, trace the exact path of the bad data:

```
[Request/Event enters at: ]
  ??[Layer 1] ??state here: [what you found]
  ??[Layer 2] ??state here: [what you found]
  ??[Where behavior diverges from expected] ??state here: [what you found]
  ??[Where the symptom manifests]
```

Identify the **exact file:line** where the wrong thing happens. This is the root cause.

---

## Step 5 ??Fix (only after root cause confirmed)

**Minimal fix** ??change only what's necessary to address the root cause, not the symptom.

Before writing the fix, state:
- "Root cause: [exact description]"
- "Fix: [what will change and why this addresses the root cause, not just the symptom]"
- "Does not fix: [what this won't change]"

```bash
git add -p   # stage only the fix
git commit -m "fix: [root cause in plain English]\n\nInvestigation: [what was found and where]"
```

**Write a regression test immediately after:**
- The test must fail before the fix and pass after
- Tests the root cause, not the symptom
- Commit: `git commit -m "test: regression for [root cause]"`

---

## Step 6 ??Verify

Reproduce the original symptom after the fix. Confirm it's gone.

If the symptom persists: you may have fixed a symptom, not the root cause. Go back to Step 2 with updated hypotheses.

---

## Step 7 ??Escalation (after 3 failed attempts)

If three different fixes have been tried and none resolved the symptom:

```
??ESCALATION ??3 attempts failed

Attempts:
1. [Fix 1] ??what changed ??result: [what happened]
2. [Fix 2] ??what changed ??result: [what happened]
3. [Fix 3] ??what changed ??result: [what happened]

Remaining hypotheses:
H?: [hypothesis] ??need to test: [what information/access/expertise is required]

Current best understanding:
The root cause is likely in [area], but I cannot verify without [specific missing info].

Recommended next step:
[Specific action: add more logging, check external service, get access to prod logs, pair with someone who knows the system]
```

**STOP HERE.** Do not attempt a 4th fix.

---

## Log + unfreeze reminder

```bash
echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"skill\":\"investigate\",\"branch\":\"$(git branch --show-current 2>/dev/null || echo 'N/A')\",\"outcome\":\"success\",\"repo\":\"$(basename $(git rev-parse --show-toplevel 2>/dev/null) 2>/dev/null || echo 'N/A')\"}" >> ~/.mystack/timeline.jsonl
```

After investigation completes: "Investigation complete. Auto-freeze is still active. Run `/stacksmith-safety off` to remove edit restrictions."

