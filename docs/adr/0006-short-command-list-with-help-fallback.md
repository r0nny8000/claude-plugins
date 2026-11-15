# 0006 scalable-cli lists 3 read commands and finds the rest in sc's help

Status: accepted
Date: 2026-11-15

## Context

ADR 0005 removed every copied `sc` command from the skill: Claude discovers
commands from `sc capabilities --json` and `sc <command> --help` of the
installed `sc`. For the most common requests that costs a turn each time. In
the 2026-11-01 portfolio runs Claude called `sc capabilities --json` before
`sc broker overview --json`, although the answer never changes between
runs. Requests outside the common ones still need discovery, and Claude had
no guidance on which help form to use or when the web manual is worth a
fetch.

## Alternatives

| Option                                                              | Verdict  | Reason                                                                                         |
|---------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------|
| Keep ADR 0005 as is: discover every command                         | rejected | An extra help call for every portfolio, cash or holdings question                              |
| Copy the full command list into the skill                           | rejected | Goes stale with each `sc` release, the problem ADR 0005 solved                                 |
| Name 3 basic read commands; help first, manual from `main` fallback | chosen   | Common requests run directly; the list is small enough to keep current; the rest stays current |

## Decision

- SKILL.md names exactly 3 read commands, run directly without help first:
  `sc broker overview --json`, `sc broker cash-breakdown --json`,
  `sc broker holdings --json`. No other file lists commands.
- Any other request: Claude uses the installed `sc`'s help first
  (`sc --help`, `sc help <command>`, `sc <command> --help` or `-h`,
  `sc capabilities --json`) and composes the command with `--json`.
  SKILL.md's "Getting help" section says which form shows what.
- Only if the help doesn't answer it, Claude fetches the manual from the
  `main` branch of upstream, never a copy. If that fetch fails, it says so,
  gives the link and stops without running a guessed command.

This supersedes ADR 0005's "no command copies" rule for these 3 commands;
the rest of ADR 0005 stands.

## How the list stays current

- A listed command missing from `sc capabilities --json` or its help means
  the list is out of date: Claude falls back to help and tells the user.
- `evals/check_portfolio_trigger.py` fails when the listed path calls help,
  capabilities or WebFetch before `sc broker overview --json`;
  `evals/check_command_discovery.py` checks that an unlisted request (a
  quote) goes through help first.

## Consequences

- An `sc` release that renames one of the 3 commands needs a skill update;
  until then the out-of-date path above applies.
