---
status: goal-ready
priority: medium
acceptance: 3 of 3 fresh `claude -p "What's my portfolio worth?"` runs with the finance plugin call `sc broker overview --json`, shown by `uv run python evals/check_portfolio_trigger.py`
---

# Goal: scalable-cli answers the portfolio question with sc

## Goal

In a real session with `sc` installed and logged in, "What's my portfolio
worth?" reliably makes Claude call `sc broker overview --json` through the
`finance:scalable-cli` skill; if it doesn't, the skill is fixed until it does.

## Context

- Repo state: branch `add-finance-plugin`; the plugin was added in 84c2384,
  ADR 0004 in b8b05ff, the skill backlog item in 59e3d96.
- Depends on `docs/backlog/goal-scalable-cli-skill.md` being done (the file is
  deleted when it is). That item builds SKILL.md, the check script and the
  references.
- Relevant files: `plugins/finance/skills/scalable-cli/SKILL.md` (its
  `description` decides triggering), `evals/measure_triggers.py` (reads
  tool calls from `claude -p --output-format stream-json --verbose`; reuse
  that approach).
- Decisions to respect: ADR 0004 (skills check and guide, never install);
  CLAUDE.md (ask before a plugin version bump; out of scope here).
- Verified facts (2026-10-21): `claude -p` supports `--plugin-dir`,
  `--output-format stream-json`, `--allowedTools` and `--max-turns`
  (`claude --help`, v2.1.306). `sc` was not installed when this goal was
  written, so the trigger check has never run.
- Files left by validation runs: none.

## Acceptance checklist

- [ ] Preconditions hold — proven by `command -v sc`, `sc whoami >/dev/null && echo logged-in` (prints only `logged-in`), and `test ! -e docs/backlog/goal-scalable-cli-skill.md && echo skill-item-done`
- [ ] Triggering is reliable — proven by `uv run python evals/check_portfolio_trigger.py`, which runs 3 fresh `claude -p "What's my portfolio worth?" --plugin-dir plugins/finance --output-format stream-json --verbose` sessions, prints only the Bash commands each one called, and ends with `3/3 PASS`
- [ ] The check script is tested — proven by `uv run pytest` exiting 0, with tests for the stream-json parsing in `tests/`
- [ ] The plugin still validates — proven by `claude plugin validate --strict plugins/finance` printing `Validation passed`

## Verification

Run `uv run pytest`, `claude plugin validate --strict plugins/finance` and
`uv run python evals/check_portfolio_trigger.py` last, after the final
change, and show their output in the transcript.

## Guardrails

- No test is deleted, skipped, or weakened to make a check pass.
- No edits outside `plugins/finance/skills/scalable-cli/`, `evals/` and
  `tests/`, except this goal file (see "When done").
- Read-only `sc` only: the test sessions get `--allowedTools` for read
  commands only; never run `sc login`, trades or savings-plan changes.
- No account data in Git: never print or store `sc` output in tracked
  files; write raw stream-json to a temp directory outside the repo; stage
  explicit paths only.
- No new dependencies: standard library and tools already in
  `pyproject.toml`.

## Out of scope

- Installing or updating `sc`, running `sc login`.
- Building the skill (`docs/backlog/goal-scalable-cli-skill.md`).
- Bumping the version in `plugins/finance/.claude-plugin/plugin.json`.
- Triggering for prompts other than "What's my portfolio worth?".

## Approach hints

- If a precondition fails, show it and stop; don't work around it.
- Count a run as a hit if any Bash call in it contains `sc broker overview`
  with `--json`; the skill may run its install check first.
- To fix misses, change the skill's `description` and workflow, then rerun
  all 3 sessions.

## When done

Ask the user whether to delete this file. Deleting is fine: it stays in git
history if it was committed.

## Open questions

None

## Condition

```text
Preconditions hold: `command -v sc` finds sc, `sc whoami >/dev/null && echo logged-in` prints logged-in, and docs/backlog/goal-scalable-cli-skill.md no longer exists; if any fails, show it and stop. Then `uv run python evals/check_portfolio_trigger.py` shows 3 of 3 fresh `claude -p "What's my portfolio worth?" --plugin-dir plugins/finance` runs calling `sc broker overview --json` and prints 3/3 PASS; `uv run pytest` exits 0 with tests for the check script; `claude plugin validate --strict plugins/finance` passes. Guardrails: no test deleted, skipped or weakened; edits only in plugins/finance/skills/scalable-cli/, evals/, tests/ and this goal file; read-only sc commands only, never sc login, trades or savings-plan changes; never print or commit sc output or account data, raw output goes to a temp dir outside the repo; no new dependencies. Out of scope: installing sc or logging in, building the skill, version bump, other prompts. Show the output of each check in the transcript. Or stop after 20 turns and report what remains.
```
