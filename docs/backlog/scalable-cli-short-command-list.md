---
status: open
priority: medium
acceptance: scalable-cli stores only a short list of the most used basic sc read commands; for any other request it composes the command from sc's own help first and fetches the current upstream manual on GitHub only when the help isn't enough; an eval shows both paths
---

# scalable-cli: store a few basic commands, look up the rest in the manual

## Goal

Don't implement or list every `sc` function in the skill. Store only a
small number of the most used basic read commands, so common questions
are answered fast. For everything else, use `sc --help`, `sc <command> --help`, `sc capabilities`, and check the upstream manual on GitHub to find the best command for the user's request, and always use
the latest version of that manual.

## Current state (checked 2026-11-01)

| Item                     | State                                                                 |
| ------------------------ | --------------------------------------------------------------------- |
| `references/commands.md` | Lists no commands; says to ask the installed `sc` instead (ADR 0005)  |
| Discovery order today    | `sc capabilities --json`, then `sc <command> --help`, then the manual |
| ADR 0005                 | Rejected keeping command copies because they go stale                 |

Upstream manual:
https://github.com/ScalableCapital/scalable-cli/blob/main/public-docs/commands.md

## Evidence from the portfolio-trigger goal (2026-11-01)

In 3 of 3 runs of `evals/check_portfolio_trigger.py`, asking "What's my
portfolio worth?" led to the same commands in the same order:

1. The skill's check script (`check_install.py`)
1. `sc capabilities --json`
1. `sc broker overview --json`
1. `sc broker cash-breakdown --json`

So Claude already finds the basic commands through `sc`'s help. This item
makes them explicit in the skill anyway, so the common questions don't
depend on discovery.

`sc broker cash-breakdown --json` reads only, but it was blocked because
the eval's `ALLOWED_TOOLS` list doesn't include it. The eval's checks
don't depend on it. When the short list is final, add its commands to
`ALLOWED_TOOLS` too.

## Changes

- Add a short list of basic read commands to the skill. Keep it small.
  Start with the two the runs used: `sc broker overview --json` and
  `sc broker cash-breakdown --json`; candidates to add are holdings and
  transactions. Name them in `SKILL.md` itself, not only in
  `references/commands.md`, so Claude sees them without opening another
  file.
- For any request the short list doesn't cover, use the installed `sc`'s
  own help first, then the upstream manual, then anything else (decided
  2026-11-01):
  1. `sc capabilities` lists the CLI's capabilities.
  1. `sc help <subcommand>` or `sc <subcommand> --help` prints the full
     help; `-h` prints a summary.
  1. Only if the help doesn't answer it: fetch the upstream manual from
     the `main` branch, never a cached or copied version.
- Compose the command from what the help shows, to fit the user's
  request (subcommand, flags, `--json`).
- Keep the read-only rules in `safety.md` as they are.

From `sc --help` output the user shared (2026-11-01, version not noted):

```
capabilities  List CLI capabilities
help          Print this message or the help of the given subcommand(s)

Options:
  -h, --help
          Print help (see a summary with '-h')
```

## Open questions

- How many commands is "a small number", and which ones? Base the pick on
  the questions users ask most.
- If the help doesn't answer it and the manual fetch fails: give the link
  and stop, or ask the user?
- This partly reverses ADR 0005 (no command copies). Write a new ADR that
  supersedes that part, and say how the short list is kept current.
- Ask about the `finance` plugin version bump (CLAUDE.md).

## Acceptance criteria

- `SKILL.md` names the short list explicitly; the skill lists no other
  commands.
- A question covered by the list runs the listed command without
  fetching the manual.
- A question outside the list makes Claude run `sc`'s help first and
  compose a read command from it; it fetches the current manual only
  when the help doesn't answer the question.
- Evals cover both paths and pass.
