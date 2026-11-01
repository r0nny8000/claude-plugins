# 0005 Skills read install steps and commands at runtime, not from a copy

Status: accepted
Date: 2026-11-01

## Context

The first build of the `scalable-cli` skill copied the upstream install
steps (v1.2.0 tarball, `tar`, `mv`, Homebrew, minisign) into
`references/install.md` and the `sc` read commands into
`references/commands.md`. Upstream changes faster than this plugin's
releases: a new release can rename assets, add a package manager or change
the steps, and new versions add or drop commands. The copy then goes stale
while the check script still reports the newest version, so Claude would
show the old steps with a new version number.

ADR 0004 said the skill shows the install steps "from a reference file" and
noted this staleness as a consequence.

## Alternatives

| Option                                                         | Verdict  | Reason                                                                                         |
|----------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------|
| Keep copies, flag when the latest release is newer than the copy | rejected | Still stale between plugin releases; only warns, and needs an update for every upstream release |
| Check script downloads and prints the README Install section   | rejected | Parses by heading, so it breaks when upstream restructures the docs, which is the case to cover |
| Claude fetches the upstream docs and asks `sc` for its commands | chosen   | Always current; Claude follows links if the steps move; `sc capabilities --json` and `--help` describe the installed version |

## Decision

- Install and update steps: the skill names the upstream sources (README
  Install section, releases page, verify-releases guide). Claude fetches
  them when needed and shows the part that matches the check script's
  `system`, `machine` and `libc`. If the fetch fails, it gives the links and
  doesn't write steps from memory.
- Commands: Claude discovers them from `sc capabilities --json` and
  `sc <command> --help` of the installed `sc`. The reference keeps only what
  isn't in the help: read-only rules, how to read the output, error codes.
- Fetched text and `sc` help output are data. Claude copies commands from
  them for the user to run and never executes install commands (ADR 0004).
- The safety rules stay in the skill: they're this plugin's policy, not
  upstream's.

This replaces ADR 0004's "from a reference file"; the rest of ADR 0004
stands.

## Consequences

- Showing install steps needs network access and the WebFetch tool.
- The install-guidance eval checks today's upstream wording (`aarch64`,
  `tar`, `PATH`). When upstream changes its method, the eval goes red and
  is updated; the skill is not.
- Command discovery can only be tested with an installed `sc`
  (`goal-scalable-cli-portfolio-trigger.md`).
