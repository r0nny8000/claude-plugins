---
status: open
priority: medium
acceptance: Every merge to main that changes a plugin produces a release with a tag and a version bump in that plugin's plugin.json, with no manual step; a test merge shows it working
---

# Release always when merged to main

## Goal

Every merge to `main` that changes a plugin ships a release, so installed
users get the update. Nobody has to remember to bump or tag by hand.

## Current state (checked 2026-11-01)

| Item                    | State                                                             |
| ----------------------- | ----------------------------------------------------------------- |
| CI                      | None: no `.github/` folder                                        |
| Git tags                | None                                                              |
| GitHub releases         | None (`gh release list` returns nothing)                          |
| Plugin versions         | `ai-engineer` 0.1.3, `finance` 0.1.0, in each `plugin.json`       |
| Version bump today      | Manual; CLAUDE.md says to ask patch/minor/major before committing |

Installed users only receive an update when the `version` in
`plugin.json` changes, so a release without a bump does not reach them.

## Open questions

- Who picks patch/minor/major: conventional commit messages, a PR label,
  or the bump is still asked during the change and CI only tags and
  releases?
- Release per plugin (tag like `finance-v0.2.0`) or one repo-wide release?
- Merges that change only docs or tests: skip the release?
- Update the CLAUDE.md versioning rule to match. Record the chosen
  approach as an ADR.

## Acceptance criteria

- A GitHub Actions workflow runs on every push to `main`.
- For each changed plugin it ensures a new version, creates a tag and a
  GitHub release.
- Merges that touch no plugin create no release.
- A test merge to `main` shows the release created end to end.
