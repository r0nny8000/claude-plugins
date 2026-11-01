---
status: open
priority: medium
acceptance: scalable-cli stores only a short list of the most used basic sc read commands; for any other request it composes the command from sc's own help first and fetches the current upstream manual on GitHub only when the help isn't enough; an eval shows both paths
---

# scalable-cli: store a few basic commands, look up the rest in the manual

## Goal

Don't implement or list every `sc` function in the skill. Store only a
small number of the most used basic read commands, so common questions
are answered fast. For everything else, check the upstream manual on
GitHub to find the best command for the user's request, and always use
the latest version of that manual.

## Current state (checked 2026-11-01)

| Item                     | State                                                                 |
| ------------------------ | --------------------------------------------------------------------- |
| `references/commands.md` | Lists no commands; says to ask the installed `sc` instead (ADR 0005)  |
| Discovery order today    | `sc capabilities --json`, then `sc <command> --help`, then the manual |
| ADR 0005                 | Rejected keeping command copies because they go stale                 |

Upstream manual:
https://github.com/ScalableCapital/scalable-cli/blob/main/public-docs/commands.md

## Changes

- Add a short list of basic read commands to `references/commands.md`
  (for example overview, holdings, cash, transactions). Keep it small.
- For any request the short list doesn't cover, use the installed `sc`'s
  own help first, then the upstream manual, then anything else (decided
  2026-11-01):
  1. `sc capabilities` lists the CLI's capabilities.
  2. `sc help <subcommand>` or `sc <subcommand> --help` prints the full
     help; `-h` prints a summary.
  3. Only if the help doesn't answer it: fetch the upstream manual from
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

- `references/commands.md` holds the short list and no other commands.
- A question covered by the list runs the listed command without
  fetching the manual.
- A question outside the list makes Claude run `sc`'s help first and
  compose a read command from it; it fetches the current manual only
  when the help doesn't answer the question.
- Evals cover both paths and pass.
