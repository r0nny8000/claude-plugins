# Goal file template

The goal is a backlog item at `docs/backlog/goal-<slug>.md`: a short YAML
header (status, priority, acceptance) followed by the brief. Fill every
section. `## Condition` is the compact condition the evaluator ends up judging;
the rest is context the executing session reads first. Keep `## Open
questions` as `None` before handoff.

The validator (`scripts/validate_goal.py`) parses this structure: the H2
headings below, checklist items as `- [ ]`, and the condition inside the first
fenced `text` block under `## Condition`. The YAML header is ignored by it.

````markdown
---
status: goal-ready
priority: <low | medium | high>
acceptance: <one line: the end state and the command that proves it>
---

# Goal: <short title>

## Goal

<One sentence: the outcome, not the steps.>

## Context

- Repo state: <branch, clean tree, last relevant commit>
- Relevant files: <paths and interfaces>
- Decisions to respect: <docs/adr/NNNN-*.md, CLAUDE.md rules>
- Verified facts: <what the definer checked and how>
- Files left by validation runs: <uv.lock, caches, or none>

## Acceptance checklist

- [ ] <Criterion> — proven by `<command>` <expected result>
- [ ] <Criterion> — proven by `<command>` <expected result>

## Verification

<The final end-to-end check, e.g. `uv run pytest` exits 0, and the instruction
to show its output in the transcript.>

## Guardrails

- No test is deleted, skipped, or weakened to make a check pass.
- No edits outside <paths>, except this goal file (see "When done").
- <Other invariants: public API, migrations, dependencies, git actions.>

## Out of scope

- <Things that look related but must not be done in this goal.>

## Approach hints

- <Optional, short. Hints, not a step list.>

## When done

Ask the user whether to delete this file. Deleting is fine: it stays in git
history if it was committed.

## Open questions

None

## Condition

```text
<End state> as shown by `<command>` <result>; <checklist items as one line
each>; guardrails: <compact invariants, incl. no test deleted, skipped or
weakened>; out of scope: <compact list>. Show the output of each check in the
transcript. Or stop after <N> turns and report what remains.
```
````
