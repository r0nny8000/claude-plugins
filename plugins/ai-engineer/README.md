# ai-engineer

Claude Code skills for AI engineering work. Install it from the
[r0nny8000-plugins marketplace](../../README.md#install).

## Skills

| Skill        | Command         | Also triggers on                                   | What it does                                                              |
|--------------|-----------------|----------------------------------------------------|---------------------------------------------------------------------------|
| goal-crafter | `/goal-crafter` | "define a goal", "write a /goal", "prepare a goal" | Recon, validation, interview rounds, writes and lints the goal file, prints the `/goal` line |

The full name is `/ai-engineer:goal-crafter`; the short name works as long as
no other skill shares it.

## goal-crafter

`/goal <condition>` keeps Claude working until a separate evaluator model
judges the condition met. That evaluator sees only the condition and the
transcript, so vague goals spin or stop early.

goal-crafter works like a crafting table: the interview collects the
ingredients (acceptance criteria, checks, guardrails, out of scope, a turn
budget), the template arranges them, and out comes a validated goal file,
`docs/backlog/goal-<slug>.md`, as a normal backlog item.

### Workflow

1. `/goal-crafter fix the login timeout bug` and answer the questions.
2. Start a fresh session (`/clear` or a new `claude`).
3. Paste the printed line:
   `/goal @docs/backlog/goal-<slug>.md Read it first, then work until its Condition holds. Show each check's output. Stop at the turn limit it names.`
4. Switch to auto mode first for an unattended run.
5. When the goal is met, the session asks whether to delete the goal file.
   Deleting is fine; git history keeps it if it was committed.

A skill can't run the built-in `/goal` itself, so step 3 is one paste. The
reasoning is in [docs/adr/0002-single-skill-goal-file-in-backlog.md](../../docs/adr/0002-single-skill-goal-file-in-backlog.md)
(which supersedes part of [0001](../../docs/adr/0001-plugin-with-nextgoal-handoff.md)).

### Requirements

| Requirement                        | Why                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------|
| Claude Code with `/goal`           | Tested on 2.1.296; claude.ai chat has no `/goal` and no local repo                       |
| Trusted folder, hooks enabled      | `/goal` is unavailable under `disableAllHooks` or `allowManagedHooksOnly`                 |
| `python` or `python3` (3.11+)      | The goal-file linter; `scripts/validate_goal.sh` uses `python` if present, else `python3` |
| `git`                              | Claude Code clones the plugin from GitHub                                                 |

Lint a goal file by hand:

```bash
python plugins/ai-engineer/scripts/validate_goal.py docs/backlog/goal-<slug>.md
```
