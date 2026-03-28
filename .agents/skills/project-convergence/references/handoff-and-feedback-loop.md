# Handoff and Feedback Loop

Convergence is not a one-time setup. Re-sync the control surface whenever the project state changes.

## Update Loop

After each milestone, blocker, or handoff:
1. Update `delivery-plan.md`
2. Confirm the next OpenSpec change
3. Update `AGENTS.md` if operating rules changed
4. Leave `CLAUDE.md` alone unless its pointer is wrong

## Minimum Handoff Payload

Every handoff should include:
- current phase
- blocker status
- next verifiable output
- next OpenSpec change
- decision delta since previous handoff
- source links for critical context
- any changed operating rule

## Blocker Handling

When blocked:
- record the blocker in `delivery-plan.md`
- state what dependency is missing
- state what can still proceed
- state whether the next OpenSpec change should change

Do not leave blockers implicit in chat history.

## Verification Checkpoints

Before handing off, confirm:
- the plan reflects the latest state
- the named next change still matches reality
- the next output is checkable
- no critical rule exists only in ephemeral chat context
- no critical decision exists only in chat memory without Decision Log and Source Links

## Failure Signals

Re-run the loop immediately if:
- two agents disagree on what comes next
- the repo has progress but no updated handoff artifact
- the active change no longer matches the stage objective
- a new blocker invalidates the prior next step
- proposal-to-milestone traceability is missing
