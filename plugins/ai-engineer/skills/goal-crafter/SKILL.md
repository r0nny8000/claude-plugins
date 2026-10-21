---
name: goal-crafter
description: Interview the user to turn a task into a strong /goal condition and write it as a backlog file docs/backlog/goal-{slug}.md. Researches the repo (git, README, CLAUDE.md, docs/adr, docs/backlog, tests) first, validates claims, then asks pick-don't-type questions about acceptance criteria, verification, guardrails, out of scope, and turn budget. Ends with a short `/goal @file ...` line to paste. Use this whenever the user wants to define, write, draft, refine, or prepare a goal, a /goal condition, or a completion condition, or wants Claude to work autonomously until something is done, even if they don't say "/goal".
argument-hint: "[task description]"
allowed-tools: Bash(sh ${CLAUDE_PLUGIN_ROOT}/scripts/validate_goal.sh *) Bash(git status *) Bash(git branch *)
---

# Goal crafter

Turn a task into a goal file, `docs/backlog/goal-<slug>.md`, that `/goal` can
run.

Why this exists: `/goal` keeps Claude working until a separate small model
judges the condition met. That evaluator sees only the condition and the
transcript; it runs no tools and reads no files. Vague conditions either spin
forever or clear at a random point. A good goal has one measurable end state,
a check command per criterion, explicit guardrails, and a stop clause. Read
[references/best-practices.md](references/best-practices.md) before drafting.

The goal file is a normal backlog item (YAML header with status, priority,
acceptance), so it follows the project's backlog convention and stays
recoverable from git history after it is deleted. Execution happens in a fresh
session, because a clean context focused on the spec outperforms a long
session full of interview chatter (Anthropic best practice). This skill never
starts the goal itself; it writes the file and hands over one short line.

## 1. Intake

The task is: $ARGUMENTS

If that is empty, ask the user for the task in one plain sentence. If a
`docs/backlog/goal-*.md` file for the same task already exists, ask whether to
refine it or replace it.

## 2. Recon (Explore subagent)

Spawn one Explore subagent so file dumps stay out of this conversation. Give
it the task and ask for a fact sheet of at most ~40 lines covering:

- git: is it a repo, branch, clean or dirty tree, last 10 commit subjects
- README, CLAUDE.md: purpose, run and test instructions, working rules
- docs/adr/: decisions relevant to the task (file names + one line each)
- docs/backlog/: related open items, and whether the folder exists
- test, lint, typecheck, build commands (pyproject.toml, package.json,
  Makefile, CI config) and whether tests exist for the affected area
- files and interfaces the task will likely touch

If the task depends on an external library or API, also look up its current
docs (WebSearch/WebFetch) so criteria reflect real behavior.

## 3. Validate before asking

Turn recon into checked facts. Run the test command once (read-only, quick
subset if the suite is long) to learn whether it works today and what the
baseline is. Confirm that files the user mentioned exist. A criterion built on
a command that doesn't run will make the goal impossible, and the user would
only find out after many turns.

Running checks can leave files behind (`uv run` creates `uv.lock`, test runs
create caches). Compare `git status` before and after. Don't delete what
appeared; list it in the brief's Context and tell the user, because a
guardrail like "edits only in src/" would otherwise trip over it.

Tell the user in a few lines what you found and what you validated.

## 4. Interview

Run the rounds from [references/interview.md](references/interview.md):
Goal, Acceptance checklist, Verification, Guardrails, Out of scope, Budget
and mode. Each round uses the same loop: draft from facts, ask with
AskUserQuestion (recommended option first, multiSelect where choices
combine), show the section as a short table, check the quality bar.

Pre-fill options from recon so the user picks instead of types. Skip
questions that recon already answers and state the assumption instead. If an
answer contains a red flag (subjective word, external dependency, irreversible
action), probe it as described in the reference.

## 5. Write and lint

Pick a short kebab-case slug from the task and write
`docs/backlog/goal-<slug>.md` (create `docs/backlog/` if it is missing) using
[references/template.md](references/template.md). The `## Condition` block is
the compact condition: readable as an instruction, under 4,000 characters,
and it must ask Claude to show each check's output in the transcript. The
guardrails must allow the executing session to read, and at the end offer to
delete, this one file, or a path guardrail like "edits only in src/" would
contradict the cleanup step.

Then run:

```bash
sh ${CLAUDE_PLUGIN_ROOT}/scripts/validate_goal.sh docs/backlog/goal-<slug>.md
```

Fix every ERROR. Discuss WARNINGs with the user only if the fix isn't obvious.
Repeat until it prints OK.

If the project is a git repo, offer to commit the goal file on its own
(`docs: add goal <slug>`). That keeps the tree clean when the goal starts and
puts the file in history before it is ever deleted.

## 6. Hand over

Show the condition and its character count. Then give the user exactly this,
with the real path filled in:

1. Start a fresh session (`/clear`, or exit and run `claude`).
2. Optionally switch to auto mode for an unattended run; /goal doesn't change
   the permission mode.
3. Paste:

```
/goal @docs/backlog/goal-<slug>.md Read it first, then work until its Condition holds. Show each check's output. Stop at the turn limit it names.
```

Why the line says "Read it first": the evaluator only sees the conversation,
and an `@` reference may not expand inside `/goal`. Making Claude read the file
in its first turn guarantees the criteria are in the transcript either way.
