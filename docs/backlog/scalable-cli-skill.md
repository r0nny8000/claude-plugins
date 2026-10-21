---
status: planned
priority: high
acceptance:
  - uv run pytest passes, including tests for the sc check script
  - claude plugin validate --strict plugins/finance passes
  - on a machine without sc, the skill reports it missing and shows the install steps for that OS without running them
  - asked "What's my portfolio worth?", Claude runs `sc broker overview --json` unprompted
  - an attempted `sc broker trade buy ...` is refused by the skill
  - no account ID, portfolio ID or real sc output is tracked by Git
---

# Build the scalable-cli skill (read-only)

## Goal

Turn the `finance:scalable-cli` scaffold into a skill that checks the `sc`
installation, knows its documentation, and answers questions about the
broker account with read-only commands only. Install handling follows
ADR 0004: check and guide, the user installs.

## Files

| File                                                         | Purpose                                                                           |
|--------------------------------------------------------------|-----------------------------------------------------------------------------------|
| plugins/finance/skills/scalable-cli/SKILL.md                 | When to use it, hard rules (read-only, user runs `sc login`), workflow, pointers  |
| plugins/finance/skills/scalable-cli/scripts/check_install.py | Installed `sc` version vs latest release vs version the references describe       |
| plugins/finance/skills/scalable-cli/references/install.md    | Install, verify, update per OS; keyring vs file session storage on headless Linux |
| plugins/finance/skills/scalable-cli/references/commands.md   | Read commands by area, with what each answers                                     |
| plugins/finance/skills/scalable-cli/references/safety.md     | Read-only rules, two-step confirmation, why `--confirm` is off-limits             |
| tests/test_check_install.py                                  | pytest tests for the check script                                                 |

## Notes

- A standalone version of this skill existed in
  `~/code/r0nny8000/scalable-cli-skill` and was deleted on 2026-10-21 without
  a backup. Rebuild from the upstream README:
  https://github.com/ScalableCapital/scalable-cli
- Bump the finance plugin version once the skill ships after a release.
