---
status: open
priority: medium
acceptance: During the goal-crafter interview, Claude shows what the finished result would look like (table, ASCII diagram or simple sketch) before the user decides on the goal and acceptance criteria; an eval shows the preview appears and stays readable in a terminal
---

# goal-crafter: show what the result would look like

## Goal

While defining a goal, show the user a picture of the finished result
whenever that's possible: a table, an ASCII diagram or a simple sketch,
as good as the terminal allows. A picture helps the user decide and
avoids misunderstandings in the goal definition.

## Current state (checked 2026-11-08)

| Where                               | What it shows today                                     |
| ----------------------------------- | ------------------------------------------------------- |
| `SKILL.md` step 4 (Interview)       | A short table of each section after the user answers    |
| `references/interview.md`, step 3   | "Show: a short table of the section as it now stands"   |
| AskUserQuestion options             | Labels and descriptions; no `preview` field used        |

So today Claude shows the goal text, not the result the goal produces.

## Changes

- Add a step to the interview (likely after the Goal round, before the
  acceptance criteria): sketch the finished result, e.g. a CLI output
  mock-up, a file tree, a before/after table, or a flow diagram.
- When options differ in how the result looks, use AskUserQuestion's
  `preview` field so the user compares them side by side.
- Skip the sketch when the result has nothing to picture (e.g. a pure
  refactor) and say so in one line.
- Keep sketches within terminal limits: monospace, no colors needed,
  narrow enough for a normal window.

## Open questions

- Which rounds get a sketch: only Goal, or also Acceptance and
  Verification?
- Should the chosen sketch go into the goal file, so the agent working
  the goal sees the same picture?
- Ask about the `ai-engineer` plugin version bump (CLAUDE.md).

## Acceptance criteria

- For a goal with a visible result, the interview shows a sketch before
  the user confirms the goal and acceptance criteria.
- Choices that change how the result looks use `preview`.
- For a goal with nothing to picture, the interview skips the sketch and
  says so.
- An eval in `evals/` covers both cases and passes.
