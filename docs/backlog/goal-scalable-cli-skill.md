---
status: goal-ready
priority: high
acceptance: the finance:scalable-cli skill is built read-only; `uv run pytest`, `claude plugin validate --strict plugins/finance`, the install-guidance session and the trigger evals (>= 90%) all pass
---

# Goal: build the scalable-cli skill (read-only)

## Goal

Turn the `finance:scalable-cli` scaffold into a read-only skill that checks
the `sc` installation and login, guides the user through what's missing, and
knows the `sc` read commands, proven by tests, a live session on this
machine and trigger evals.

## Context

- Repo state: branch `add-finance-plugin`, clean tree; scaffold in 84c2384,
  ADR 0004 in b8b05ff, this item's criteria reworked in c6d4d47. Replaces
  `docs/backlog/scalable-cli-skill.md`.
- Relevant files: `plugins/finance/skills/scalable-cli/SKILL.md` (stub),
  `plugins/finance/skills/scalable-cli/README.md` (requirements, doc links),
  `evals/measure_triggers.py` (hard-wired to goal-crafter; usage
  `<eval-set> <model> <out>`), root `README.md` (Develop section).
- Files to create: `plugins/finance/skills/scalable-cli/scripts/check_install.py`,
  `references/install.md`, `references/commands.md`, `references/safety.md`,
  `tests/test_check_install.py`, `evals/trigger-scalable-cli.json`, and a
  script for the install-guidance session in `evals/`.
- Triggering: Claude loads the skill from its `description` (signal words:
  Scalable, Scalable Capital, depot, portfolio, broker, sc CLI); the user
  can also run `/finance:scalable-cli`.
- Build method: `anthropic-skills:skill-creator`, with trigger evals.
- Decisions to respect: ADR 0004 (check and guide, never install); upstream
  README: the user runs `sc login`, enable Agentic Investing first.
- Upstream docs: https://github.com/ScalableCapital/scalable-cli (README
  sections Install, Quick start, Common commands, Configuration; latest
  release v1.1.0 on 2026-10-21).
- Verified facts (2026-10-21): `uv run pytest` gives 27 passed; this
  machine is Linux `aarch64`, Python 3.13, `sc` not installed;
  `pyproject.toml` has no runtime dependencies; `claude -p` supports
  `--plugin-dir`, `--output-format stream-json`, `--max-turns`.
- Files left by validation runs: none.

## Acceptance checklist

- [ ] Check script reports state — proven by `python -I plugins/finance/skills/scalable-cli/scripts/check_install.py` printing JSON with findings `["not_installed"]` on this machine
- [ ] Missing, outdated and logged-out states are tested — proven by `uv run pytest -v tests/test_check_install.py` passing tests for `not_installed`, `update_available` and `not_logged_in` (mocked `sc --version` / `sc whoami`)
- [ ] Whole suite green — proven by `uv run pytest` exiting 0 with at least 27 + the new tests passing
- [ ] Skill shows install steps without running them — proven by a script in `evals/` that runs `claude -p "Is sc installed?" --plugin-dir plugins/finance`, prints every Bash command called and the final answer, and ends with PASS when the answer gives the Linux aarch64 steps and no call installs anything (`sudo`, `install`, `brew`, `tar`, `gh release download`)
- [ ] Logged-out state is explained — proven by `grep -n not_logged_in plugins/finance/skills/scalable-cli/SKILL.md` showing a line that tells the user to enable Agentic Investing and run `sc login` themselves
- [ ] Read-only rules stated — proven by `grep -n -i -E 'sc login|trade|savings plan|--confirm' plugins/finance/skills/scalable-cli/SKILL.md` showing the rules that forbid them
- [ ] Trigger evals pass — proven by `uv run python evals/measure_triggers.py` on `evals/trigger-scalable-cli.json` (at least 10 should-trigger and 10 should-not prompts) for `scalable-cli` with `--plugin-dir plugins/finance`, printing a summary with passed / total >= 0.9
- [ ] goal-crafter evals still work — proven by the README's 3-argument `measure_triggers.py` command completing on a 2-query subset of `evals/trigger-goal-crafter.json` written to a temp dir
- [ ] Plugin validates — proven by `claude plugin validate --strict plugins/finance` printing `Validation passed`

## Verification

After the final change, run `uv run pytest`, `claude plugin validate
--strict plugins/finance`, the install-guidance script and the trigger
evals, and show their output in the transcript.

## Guardrails

- No test is deleted, skipped, or weakened to make a check pass.
- No edits outside `plugins/finance/skills/scalable-cli/`, `tests/`,
  `evals/` and the root `README.md`, except this goal file (see "When
  done").
- Read-only skill: SKILL.md forbids `sc login`, trades, savings-plan changes
  and `--confirm`; Claude never runs install commands itself (ADR 0004).
- `measure_triggers.py` keeps its 3-argument usage for goal-crafter.
- No new dependencies: standard library only, `pyproject.toml` unchanged.
- No account ID, portfolio ID or real `sc` output in tracked files; stage
  explicit paths only.

## Out of scope

- Bumping the version in `plugins/finance/.claude-plugin/plugin.json`.
- Anything that needs an installed, logged-in `sc` (that's
  `goal-scalable-cli-portfolio-trigger.md`).
- Installing or updating `sc`.
- A `references/automation.md` for a later automation app.

## Approach hints

- Use `anthropic-skills:skill-creator` to draft SKILL.md and the eval set.
- Detect "not logged in" with `sc whoami`; read the exact upstream behavior
  from the README instead of guessing exit codes, and note in a comment
  what was assumed.
- Keep SKILL.md short; put install steps, commands and safety rules in the
  references and link them one level deep.

## When done

Ask the user whether to delete this file. Deleting is fine: it stays in git
history if it was committed.

## Open questions

None

## Condition

```text
The finance:scalable-cli skill is built read-only and proven: `python -I plugins/finance/skills/scalable-cli/scripts/check_install.py` prints findings ["not_installed"] on this machine; `uv run pytest -v tests/test_check_install.py` passes tests for not_installed, update_available and not_logged_in (mocked sc); `uv run pytest` exits 0 with at least 27 plus the new tests; an evals/ script runs `claude -p "Is sc installed?" --plugin-dir plugins/finance`, prints every Bash command and the final answer, and ends PASS when the answer gives the Linux aarch64 steps and no call installs anything; grep shows SKILL.md maps not_logged_in to "enable Agentic Investing, run sc login yourself" and forbids sc login, trades, savings-plan changes and --confirm; `evals/measure_triggers.py` on evals/trigger-scalable-cli.json (>= 10 should, >= 10 should-not) with --plugin-dir plugins/finance prints passed/total >= 0.9; its 3-argument goal-crafter usage still completes on a 2-query subset; `claude plugin validate --strict plugins/finance` passes. Guardrails: no test deleted, skipped or weakened; edits only in plugins/finance/skills/scalable-cli/, tests/, evals/, root README.md and this goal file; Claude never runs install or sc login; no new dependencies; no account data or sc output in Git, stage explicit paths. Out of scope: version bump, real-account checks, installing sc, automation.md. Show the output of each check in the transcript. Or stop after 40 turns and report what remains.
```
