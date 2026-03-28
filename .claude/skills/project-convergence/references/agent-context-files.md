# Agent Context Files

Use `AGENTS.md` and `CLAUDE.md` for different jobs. If both files try to do everything, they drift.

## `AGENTS.md`

`AGENTS.md` is the project operating contract.

Put these items here:
- required planning artifacts
- handoff rules
- update discipline
- decision and validation expectations
- project-specific working constraints

Keep it durable. Another agent should be able to enter the repo and understand how to operate without prior chat context.

## `CLAUDE.md`

`CLAUDE.md` is the bootstrap entry point for agents that look for local instructions.

Use it to:
- tell the agent to read `AGENTS.md` first
- add only minimal bootstrap notes if needed for discovery

Do not duplicate the full contract here. Duplication creates split-brain instructions.

## Recommended Relationship

Use wording close to:

```md
# CLAUDE.md

Read `AGENTS.md` before doing any project work. Treat it as the project operating contract.
```

## Quality Checks

- `AGENTS.md` is the source of truth for operating rules.
- `CLAUDE.md` points to `AGENTS.md` and stays short.
- Updating the operating contract only requires editing one main file.
