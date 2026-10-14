---
name: goal-runner
description: Pick up a prepared NEXTGOAL.md in a fresh session, validate it, confirm with the user, load the brief into context, and print the exact /goal line to paste. Also cleans up NEXTGOAL.md after the goal is met. Use this whenever the user wants to run, start, execute, launch, or resume the next goal or NEXTGOAL.md, or asks what goal is queued, even if they don't name the file.
allowed-tools: Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/validate_goal.py *) Bash(git status *) Bash(git branch *)
---

# Goal runner

Bridge from a prepared NEXTGOAL.md to a running `/goal`.

Why it works this way: a skill can't run the built-in `/goal` command, so the
user pastes one line. Before that, this skill prints the full brief into the
conversation. That matters twice: the working Claude starts with the full
context (files, decisions, guardrails), and the `/goal` evaluator, which only
reads the transcript, can see what the criteria refer to.

## 1. Find the goal

Read NEXTGOAL.md in the project root. If it doesn't exist, say so and suggest
`/goal-definer` to create one; stop there.

If the user says the goal was achieved (or `/goal` status shows it achieved),
skip to step 5.

## 2. Pre-flight checks

Run these and collect the results:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate_goal.py NEXTGOAL.md
git status --short
git branch --show-current
```

| Check                 | Why it matters                                                         |
|-----------------------|------------------------------------------------------------------------|
| Validator prints OK   | Errors mean the goal can spin or clear wrongly; send the user back to `/goal-definer` |
| Clean working tree    | Autonomous turns mix with your uncommitted work; the diff becomes unreviewable. NEXTGOAL.md itself doesn't count |
| Not on main/master    | Easy review and rollback of everything the goal changed                |
| Fresh session         | If this conversation already holds a long interview, recommend `/clear` first |

## 3. Confirm

Show a compact summary table: goal sentence, number of acceptance items, the
verification command, guardrails, out-of-scope items, stop clause, and the
pre-flight results. Then ask with AskUserQuestion:

- Run (Recommended when all checks pass)
- Fix pre-flight issues first (e.g. create a branch, commit or stash)
- Edit the goal (go back to `/goal-definer`)
- Abort

If the user picks a fix, help with it and return to this step.

## 4. Load and hand over

Print the full NEXTGOAL.md content (all sections except `## Condition`) under
the heading "Goal brief" so it sits in the transcript.

Then get the exact condition text:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate_goal.py NEXTGOAL.md --print-condition
```

Print the paste line in its own code block, prefixed with `/goal `, exactly as
returned, without rewording, so what the user pastes is what was validated.
Remind them:

- auto mode is needed for an unattended run (/goal doesn't change permissions)
- `/goal` without arguments shows status; `/goal clear` stops it
- `/clear` would drop the goal, so don't clear mid-run

## 5. Clean up after the goal is met

When the goal is achieved, ask whether to delete NEXTGOAL.md. It is a
temporary handoff; the lasting record belongs in commits and, for significant
decisions, ADRs. Delete it only after the user agrees.
