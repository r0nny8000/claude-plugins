# 0002 One skill, goal file in docs/backlog, short /goal @file line

Status: accepted
Date: 2026-10-14
Supersedes in part: 0001 (goal-runner skill and the gitignored NEXTGOAL.md)

## Context

ADR 0001 chose two skills: `goal-definer` writing a temporary NEXTGOAL.md and
`goal-runner` reading it in a fresh session. First use showed two problems:

- The runner's namespaced command (`/goal-definer:goal-runner`) is long, and
  the user wants to type `/goal @<file>` plus a very short instruction.
- A special temporary file in the project root sits outside the project's
  own backlog convention (one Markdown file per task under `docs/backlog/`,
  YAML header, deleted when done, history kept in git).

## Alternatives

| Option                                               | Verdict  | Reason                                                                                         |
|------------------------------------------------------|----------|------------------------------------------------------------------------------------------------|
| Keep goal-runner, shorten its name                   | rejected | Still a second skill and a second step for what is one paste                                   |
| Goal file in docs/backlog/goal-<slug>.md, no runner  | chosen   | Follows the backlog convention; one skill; user pastes `/goal @file ...`                       |
| Keep NEXTGOAL.md, drop only the runner               | rejected | Special file outside the backlog convention; needs its own ignore and cleanup rules            |

## Decision

- Remove `goal-runner`. `goal-definer` is the only skill.
- The goal is written to `docs/backlog/goal-<slug>.md` with the YAML header
  (status, priority, acceptance) and the same body sections as before.
- The file is a normal committed backlog item, not git-excluded. The definer
  offers to commit it alone so the tree is clean when the goal starts.
- The definer ends with a paste line of the form
  `/goal @docs/backlog/goal-<slug>.md Read it first, then work until its
  Condition holds. Show each check's output. Stop at the turn limit it names.`
- When the goal is met, the executing session asks whether to delete the
  file; deletion is fine because history keeps it if it was committed.

## Consequences

- `@file` is not expanded inside `/goal`. Tested on 2026-10-14 with Claude
  Code 2.1.296 (`claude -p "/goal @docs/backlog/goal-marker.md Read it first
  ..."`): the transcript shows `Goal set: @docs/backlog/goal-marker.md ...` as
  literal text, and the file reached the transcript only because Claude ran
  `cat` on it in its first turn. The "Read it first" wording is therefore
  required, not decoration; a bare `/goal @file` would leave the evaluator
  without the criteria.
- The pre-flight checks the runner did (clean tree, not on main, permission
  mode) are now guidance in the definer's hand-over and the goal file's
  guardrails; nothing enforces them.
- The execution-side checks live in the goal file itself, so they are only as
  good as the interview that wrote them.
