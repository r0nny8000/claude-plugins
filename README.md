# goal-definer

A Claude Code plugin for writing strong `/goal` conditions.

`/goal <condition>` keeps Claude working until a separate evaluator model
judges the condition met. That evaluator sees only the condition and the
transcript, so vague goals spin or stop early. This plugin interviews you,
researches the project first, and writes a validated goal as a normal backlog
item, `docs/backlog/goal-<slug>.md`.

## Skill

| Skill        | Command         | Also triggers on                              | What it does                                                              |
|--------------|-----------------|-----------------------------------------------|---------------------------------------------------------------------------|
| goal-definer | `/goal-definer` | "define a goal", "write a /goal", "prepare a goal" | Recon, validation, interview rounds, writes and lints the goal file, prints the `/goal` line |

The full name is `/goal-definer:goal-definer`; the short name works as long as
no other skill shares it.

## Workflow

1. `/goal-definer fix the login timeout bug` and answer the questions.
2. Start a fresh session (`/clear` or a new `claude`).
3. Paste the printed line:
   `/goal @docs/backlog/goal-<slug>.md Read it first, then work until its Condition holds. Show each check's output. Stop at the turn limit it names.`
4. Switch to auto mode first for an unattended run.
5. When the goal is met, the session asks whether to delete the goal file.
   Deleting is fine; git history keeps it if it was committed.

A skill can't run the built-in `/goal` itself, so step 3 is one paste. The
reasoning is in [docs/adr/0002-single-skill-goal-file-in-backlog.md](docs/adr/0002-single-skill-goal-file-in-backlog.md)
(which supersedes part of [0001](docs/adr/0001-plugin-with-nextgoal-handoff.md)).

## Install

### Requirements

| Requirement                        | Why                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------|
| Claude Code with `/goal`           | Tested on 2.1.296                                                                         |
| Trusted folder, hooks enabled      | `/goal` is unavailable under `disableAllHooks` or `allowManagedHooksOnly`                 |
| `python` or `python3` (3.11+)      | The goal-file linter; `scripts/validate_goal.sh` uses `python` if present, else `python3` |
| `git` and read access to the repo  | The repo is private; Claude Code clones it with your existing git credentials            |

### From GitHub

The repo is private, so you need read access and a stored git credential.
Claude Code runs `git` without prompts. Either an SSH key loaded in
`ssh-agent` works, or HTTPS with a stored credential:

```bash
gh auth login && gh auth setup-git    # HTTPS only; skip if your SSH key works
```

Then add the marketplace and install the plugin:

```bash
claude plugin marketplace add r0nny8000/goal-definer-skill
claude plugin install goal-definer@goal-definer-marketplace
```

Without an SSH key, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`, or installs from
`/plugin` and updates fail. Get new versions with
`claude plugin update goal-definer@goal-definer-marketplace`.

### From a local clone

Load it for one session while developing:

```bash
claude --plugin-dir /path/to/goal-definer-skill
```

Or install it from the clone as a local marketplace. It then loads your
current files at every session start:

```bash
claude plugin marketplace add /path/to/goal-definer-skill
claude plugin install goal-definer@goal-definer-marketplace
```

## Develop

```bash
uv run pytest                          # validator tests
claude plugin validate --strict .      # manifest + skill frontmatter
python scripts/validate_goal.py docs/backlog/goal-<slug>.md
```

To release, bump `version` in `.claude-plugin/plugin.json`. GitHub installs
stay on their cached copy until that string changes.

Skill evals (skill-creator method) live in `evals/`: `evals.json` holds the
test prompts, `make_fixture.sh` builds the sample repo, `grade.py` scores an
iteration, `measure_triggers.py` checks signal-word triggering of the
installed plugin against `trigger-goal-definer.json`.
