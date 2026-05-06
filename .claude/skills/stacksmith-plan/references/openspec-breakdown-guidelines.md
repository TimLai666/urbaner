# OpenSpec Breakdown Guidelines

Use OpenSpec changes as the executable units of project convergence. The plan points to the next change; the change defines the next verifiable unit of work.

## Phase Kickoff Proposal Set

- At phase kickoff, you MUST create the full proposal inventory for that phase before execution starts.
- Treat missing proposal coverage as non-convergent state.
- Do not start implementation for uncovered scope.

## Breakdown Rule

Split stage work into small changes that each answer:
- what single result is being produced
- how that result will be verified
- what the next agent can pick up without re-planning the whole phase

Prefer:
- one change per capability slice
- one change per migration step
- one change per coordination or setup milestone

Avoid:
- one change for an entire phase
- one change mixing unrelated capabilities
- tasks that cannot be validated independently

## Linking Rule

For each active stage item:
- map it to one current or next OpenSpec change
- map each OpenSpec change to a milestone id
- name that change directly in `delivery-plan.md`
- keep the plan and change list in sync

## Verification Rule

Each change should end in one verifiable output:
- validated proposal
- approved design
- implemented capability
- passing test or scenario
- archived change after completion

## Readiness Gate

Phase execution starts only when:
- proposal coverage for the phase is complete
- each proposal maps to one milestone
- each proposal defines one verifiable output

## CLI and Spec Syntax

Do not duplicate OpenSpec command help here.

**REQUIRED SUB-SKILL:** Use `openspec` for:
- command selection
- proposal scaffolding
- delta authoring
- validation
- archive flow

## Quality Checks

- The next agent can pick one change id and start.
- The plan never points to a vague bucket like `backend cleanup`.
- Change size is small enough that status can be judged as done or not done.
- Proposal inventory is complete for the active phase.
- Proposal-to-milestone mapping is explicit.
