---
status: goal-ready
priority: medium
acceptance: SKILL.md names exactly 3 sc read commands, unlisted requests go through sc help first; proven by `uv run pytest` and 3/3 PASS from both `evals/check_portfolio_trigger.py` and `evals/check_command_discovery.py`
---

# Goal: scalable-cli stores 3 basic commands, finds the rest in sc's help

## Goal

The scalable-cli skill runs its 3 listed read commands directly, and for any
other request it composes the read command from the installed `sc`'s help,
fetching the upstream manual from `main` only when the help doesn't answer it.

## Context

- Repo state: branch `add-finance-plugin`; last commits add the backlog items
  and `6707dac` (portfolio-trigger check). Your uncommitted edits sit in
  `docs/backlog/scalable-cli-short-command-list.md`; this goal comes from that
  item and must not edit it.
- Relevant files: `plugins/finance/skills/scalable-cli/SKILL.md` (section
  "2. Read data" and the `description`), `references/commands.md` (discovery
  order, portfolio selection, output, errors), `references/safety.md` (write
  commands; stays unchanged), `evals/check_portfolio_trigger.py` (pattern to
  reuse: `parse_run`, `is_hit`, `ALLOWED_TOOLS`, raw stream-json in a temp dir),
  `tests/test_check_portfolio_trigger.py`.
- Decisions made while defining this goal (2026-11-15):
  - Short list, named in SKILL.md only: `sc broker overview --json`,
    `sc broker cash-breakdown --json`, `sc broker holdings --json`.
  - Any other request: `sc capabilities`, `sc help <cmd>`, `sc <cmd> --help`
    or `-h` first; compose the command from that help and add `--json`.
  - Only if the help doesn't answer it: fetch the manual from the `main`
    branch, https://github.com/ScalableCapital/scalable-cli/blob/main/public-docs/commands.md,
    never a copy. If that fetch fails: say so, give the link, and stop
    without running a guessed command.
  - New ADR `docs/adr/0006-*.md` supersedes ADR 0005's "no command copies"
    rule for these 3 commands and says how the list stays current (e.g. a
    listed command missing from `sc capabilities` or its help means: fall
    back to help and tell the user). ADR 0005 gets only a "partly superseded
    by 0006" note.
  - finance plugin version 0.1.0 to 0.2.0 (minor), asked per CLAUDE.md.
- Decisions to respect: ADR 0004 (check and guide, never install), ADR 0005
  except the part 0006 supersedes, CLAUDE.md.
- Verified facts (2026-11-15): `sc 1.2.0` is installed and logged in;
  `sc --help`, `sc help broker`, `sc broker -h` work; `sc broker --help` lists
  overview, cash-breakdown, holdings, transactions, quote and more;
  `sc broker quote --isin <ISIN> [--json]` exists; the manual URL returns
  HTTP 200. `uv run pytest` gives 38 passed; `claude plugin validate --strict
  plugins/finance` passes. In the 2026-11-01 portfolio runs Claude called
  `sc capabilities --json` before `sc broker overview --json`, so the
  tightened listed-path check fails today.
- Files left by validation runs: none.

## Acceptance checklist

- [ ] SKILL.md holds the short list — proven by `uv run pytest tests/test_skill_command_list.py` passing: the "Read data" section of SKILL.md names exactly `sc broker overview`, `sc broker cash-breakdown` and `sc broker holdings`, each with `--json`; `references/commands.md` names no other `sc broker` subcommand; SKILL.md or commands.md contains the manual URL on `main`
- [ ] Listed path skips help and the manual — proven by `uv run python evals/check_portfolio_trigger.py` ending with `3/3 PASS`, after it also fails a run with any WebFetch call or any `sc` help or `sc capabilities` call before `sc broker overview --json`, and its `ALLOWED_TOOLS` include cash-breakdown and holdings
- [ ] Unlisted path uses help first — proven by `uv run python evals/check_command_discovery.py` ending with `3/3 PASS`: 3 fresh sessions with "What's the current quote for IE00B4L5Y983?" each run an `sc` help call before `sc broker quote` with `--isin IE00B4L5Y983` and `--json`, with no WebFetch and no `mcp__` call; it prints only the Bash commands
- [ ] Both checks are tested — proven by `uv run pytest` exiting 0, with parsing and pass/fail tests for the new eval and the tightened listed-path rule in `tests/`
- [ ] The decision is recorded — proven by `ls docs/adr/0006-*.md` finding one file and `grep -n 0006 docs/adr/0005-read-tool-docs-at-runtime.md` finding the note
- [ ] Version bumped — proven by `grep '"version": "0.2.0"' plugins/finance/.claude-plugin/plugin.json` printing the line
- [ ] The plugin still validates — proven by `claude plugin validate --strict plugins/finance` printing `Validation passed`

## Verification

After the final change, run `uv run pytest`, `claude plugin validate --strict
plugins/finance`, `uv run python evals/check_portfolio_trigger.py` and
`uv run python evals/check_command_discovery.py`, and show their output in the
transcript.

## Guardrails

- No test is deleted, skipped, or weakened to make a check pass; the
  existing listed-path rules (overview with `--json`, no `mcp__` call) stay.
- No edits outside `plugins/finance/skills/scalable-cli/` (except
  `references/safety.md`, which stays unchanged), `evals/`, `tests/`, a new
  `docs/adr/0006-*.md`, a status note in `docs/adr/0005-read-tool-docs-at-runtime.md`,
  and the `version` field of `plugins/finance/.claude-plugin/plugin.json`;
  except this goal file (see "When done").
- Never edit `docs/backlog/scalable-cli-short-command-list.md`; it holds the
  user's uncommitted edits.
- Read-only `sc` only: test sessions get `--allowedTools` for read commands
  only; never run `sc login`, trades or savings-plan changes.
- No account data in Git: never print or store `sc` output in tracked files;
  raw stream-json goes to a temp directory outside the repo; stage explicit
  paths only.
- No MCP in test sessions: `ENABLE_CLAUDEAI_MCP_SERVERS=false` and
  `--strict-mcp-config`; never call the Scalable connector's tools.
- No new dependencies: standard library and pytest only.

## Out of scope

- Evals for the manual path (help not enough) and the fetch-fails path; the
  skill text describes them, but no eval runs them.
- More commands on the short list (transactions, quote, others).
- Changing `references/safety.md` or the read-only rules.
- Triggering for prompts other than the two eval prompts.
- Installing or updating `sc`, `sc login`, pushing, merging.
- `docs/backlog/restructure-project-uv-per-folder.md`.

## Approach hints

- Count as a help call any Bash command with `sc help`, `sc capabilities`, or
  an `sc` command with `--help` or ` -h`. The skill's `check_install.py` may
  run first on both paths.
- WebFetch can stay out of `--allowedTools`: a denied attempt still shows up
  as a tool_use and fails the run.
- If the listed path still calls `sc capabilities` first, make SKILL.md say
  to run a listed command directly; rerun all 3 sessions after each change.

## When done

Ask the user whether to delete this file and the source backlog item
`docs/backlog/scalable-cli-short-command-list.md`. Deleting is fine: each
stays in git history if it was committed. Ask again about the version bump
before committing (CLAUDE.md).

## Open questions

None

## Condition

```text
scalable-cli names exactly 3 read commands in SKILL.md (sc broker overview, cash-breakdown, holdings, each --json) and composes any other command from sc's help, fetching the manual from main only if the help doesn't answer it. Done when: `uv run pytest` exits 0 with tests for the short list (tests/test_skill_command_list.py), the new eval's parsing and the tightened listed-path rule; `uv run python evals/check_portfolio_trigger.py` prints 3/3 PASS while also failing any run with WebFetch or an sc help/capabilities call before sc broker overview --json; `uv run python evals/check_command_discovery.py` prints 3/3 PASS for "What's the current quote for IE00B4L5Y983?", each run calling sc help before sc broker quote --isin IE00B4L5Y983 --json, with no WebFetch and no mcp__ call; `ls docs/adr/0006-*.md` finds the ADR and `grep -n 0006 docs/adr/0005-read-tool-docs-at-runtime.md` finds the note; plugin.json version is 0.2.0; `claude plugin validate --strict plugins/finance` passes. Guardrails: no test deleted, skipped or weakened; edits only in plugins/finance/skills/scalable-cli/ (not safety.md), evals/, tests/, a new docs/adr/0006, a note in ADR 0005, the finance plugin.json version and this goal file; never edit docs/backlog/scalable-cli-short-command-list.md; read-only sc only, never sc login, trades or savings-plan changes; no sc output or account data printed or committed, raw output in a temp dir outside the repo; test sessions without MCP or claude.ai connectors; no new dependencies. Out of scope: evals for the manual and fetch-fails paths, more listed commands, safety.md, other prompts, installing sc, pushing. Show the output of each check in the transcript. Or stop after 25 turns and report what remains.
```
