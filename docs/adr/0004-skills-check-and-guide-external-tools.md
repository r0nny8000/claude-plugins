# 0004 External tools: skills check and guide, plugins don't install

Status: accepted
Date: 2026-10-21

## Context

The `finance` plugin's `scalable-cli` skill needs the Scalable CLI `sc`, a
native binary that reads and can change a broker account. It isn't on the
system by default, and installing it differs per OS: Homebrew or a PKG on
macOS, a tarball for `x86_64` or `aarch64` on Linux, plus an optional
minisign check. Before first use, the user has to enable the CLI on the
Scalable web platform and run `sc login`; upstream advises against letting
an agent log in.

Anthropic's guidance:

- Skill authoring best practices: don't assume tools are installed, list
  required packages in SKILL.md and verify they're available, and have
  scripts handle errors instead of leaving them to Claude.
- Plugin components: the LSP section says a plugin "configures the
  connection but doesn't install the server binary"; Claude Code expects it
  on the user's `PATH`.
- Plugin components: `${CLAUDE_PLUGIN_DATA}` with a `SessionStart` hook is
  the documented way to install dependencies, but its example covers
  language packages (`node_modules`), not system tools.
- Plugin components: a plugin can ship executables in `bin/`, but claude.ai
  and Cowork don't install a plugin that has one.

## Alternatives

| Option                                                   | Verdict  | Reason                                                                                                                 |
|----------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------------|
| Ship the binary in the plugin's `bin/`                   | rejected | Redistributes a third-party binary, so it's no longer an official build; one per platform; blocks claude.ai and Cowork |
| `SessionStart` hook that downloads and installs the tool | rejected | Silently fetches software with account access on every session; needs `brew` or a writable `PATH` folder               |
| Skill checks for the tool and shows install steps per OS | chosen   | Matches the best practices; the user keeps control over where the binary comes from and runs the install               |

## Decision

- Plugins in this repo don't install external tools and don't bundle
  third-party binaries.
- A skill that needs a tool runs a check script first (for `sc`:
  `check_install.py`, which reports `not_installed` and `update_available`).
- If the tool is missing or outdated, the skill shows the install steps for
  the user's OS from a reference file. The user runs them. Claude runs an
  install command only after the user confirms it.
- Each skill's README lists its requirements for humans.

## Consequences

- A first run on a fresh machine needs a manual install step.
- Install steps live in the skill's reference files and go stale when
  upstream changes; the check script's `docs_outdated` finding flags this
  for `sc`.
- Language-package dependencies, such as Python packages for a skill's own
  scripts, aren't covered here. A `${CLAUDE_PLUGIN_DATA}` install hook stays
  possible for those.

## Sources

- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- https://code.claude.com/docs/en/plugins/components
- https://github.com/ScalableCapital/scalable-cli
