---
status: open
priority: medium
acceptance: A written workflow covers story-to-feature, bugs and upgrades, and how to add a new role; an agent follows it on every run without being reminded
---

# Workflow for new features, new roles, bugs and upgrades

## Goal

Define one workflow that takes work from the first story to a shipped
feature, and covers the other kinds of change too. An agent runs it
always, not only when asked.

## Scope

| Path          | Starts with                    | Ends with                          |
| ------------- | ------------------------------ | ---------------------------------- |
| New feature   | A user story                   | A merged, tested feature           |
| New role      | The need for a new role        | The role defined and usable        |
| Bug           | A bug report                   | A failing test turned green, fixed |
| Upgrade       | A dependency or tool update    | The upgrade merged, tests green    |

## Open questions

- What is a "role" here: an agent role (planner, developer, reviewer), a
  plugin, or a skill?
- "Agent should run always": a hook, a skill that triggers on every task,
  or a CLAUDE.md rule? Decide and record it as an ADR.
- Where does the workflow live: a new plugin, a skill in `ai-engineer`, or
  a doc?
- How does it fit with the existing backlog, ADR and goal-crafter flow?

## Acceptance criteria

- The workflow is written down for all four paths in the table.
- Each path names its start trigger, its steps and its done condition.
- A fresh session given a story, a bug or an upgrade follows the workflow
  without being told to.
