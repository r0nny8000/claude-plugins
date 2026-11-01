---
status: open
priority: medium
acceptance: Each plugin or skill with Python code has its own uv project and runs its tests with `uv run pytest` from its own folder; no skill imports, calls or references files of another skill; the repo root holds no uv project
---

# Restructure the project: uv per sub folder, no dependencies between skills

## Goal

Move the uv setup from the repo root into the sub folders, so each part
installs and tests on its own. Keep every skill self-contained: no skill
depends on another skill.

## Current state (checked 2026-11-01)

| Item                                 | Where it lives now                                             |
| ------------------------------------ | -------------------------------------------------------------- |
| `pyproject.toml`, `uv.lock`, `.venv` | Repo root, one project for everything                          |
| Root `pyproject.toml` description    | Still describes only the goal plugin (outdated)                |
| Tests                                | `tests/` at the root, covering both plugins                    |
| Evals                                | `evals/` at the root, covering both plugins                    |
| goal-crafter script                  | `plugins/ai-engineer/scripts/` (plugin level, not skill level) |
| scalable-cli script                  | `plugins/finance/skills/scalable-cli/scripts/` (skill level)   |

## Open questions

- Granularity: one uv project per plugin, or per skill?
- Where do tests and evals go: next to each plugin or skill, or stay at
  the root?
- Should `plugins/ai-engineer/scripts/` move into the goal-crafter skill
  folder to match scalable-cli?
- Record the chosen layout as an ADR.

## Acceptance criteria

- The repo root has no `pyproject.toml`, `uv.lock` or `.venv`.
- Each part with Python code has its own `pyproject.toml` and passes
  `uv run pytest` from its own folder.
- No skill reads, runs or imports a file from another skill's folder.
- README explains the new layout and how to run each part's tests.
