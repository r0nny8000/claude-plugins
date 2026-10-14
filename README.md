# goal-definer

A Claude Code plugin for writing strong `/goal` conditions.

`/goal <condition>` keeps Claude working until a separate evaluator model
judges the condition met. That evaluator sees only the condition and the
transcript, so vague goals spin or stop early. This plugin interviews you,
researches the project first, and writes a validated goal to `NEXTGOAL.md`. A
fresh session then picks it up.

## Skills

| Skill        | Command          | Also triggers on                               | What it does                                                          |
|--------------|------------------|------------------------------------------------|-----------------------------------------------------------------------|
| goal-definer | `/goal-definer`  | "define a goal", "write a /goal", "NEXTGOAL"   | Recon, validation, interview rounds, writes and lints NEXTGOAL.md     |
| goal-runner  | `/goal-runner`   | "run the next goal", "start NEXTGOAL"          | Pre-flight checks, confirmation, loads the brief, prints the /goal line |

Full names are `/goal-definer:goal-definer` and `/goal-definer:goal-runner`;
the short names work as long as no other skill shares them.

## Workflow

1. `/goal-definer fix the login timeout bug` and answer the questions.
2. `/clear` (or start a new `claude` session).
3. `/goal-runner`, confirm, then paste the printed `/goal ...` line.
4. Switch to auto mode for an unattended run.

A skill can't run the built-in `/goal` itself, so step 3 ends with one paste.
The reasoning is in [docs/adr/0001-plugin-with-nextgoal-handoff.md](docs/adr/0001-plugin-with-nextgoal-handoff.md).

## Install

Load it for one session while developing:

```bash
claude --plugin-dir /path/to/goal-definer-skill
```

Install it permanently from this repo as a local marketplace:

```bash
claude plugin marketplace add /path/to/goal-definer-skill
claude plugin install goal-definer@goal-definer-marketplace
```

## Develop

```bash
uv run pytest                          # validator tests
claude plugin validate --strict .      # manifest + skill frontmatter
python scripts/validate_goal.py NEXTGOAL.md
```

Skill evals (skill-creator method) live in `evals/`: `evals.json` holds the
test prompts, `make_fixture.sh` builds the sample repo, `grade.py` scores an
iteration.
