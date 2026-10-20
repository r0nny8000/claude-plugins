---
status: proposed
priority: high
acceptance:
  - "`uv run pytest` passes with the new paths"
  - "`claude plugin validate .` and `claude plugin validate ./plugins/ai-engineer` print `✔ Validation passed`"
  - "A clean install from GitHub (`marketplace add r0nny8000/claude-plugins`, `install ai-engineer@r0nny8000-plugins`) lists `/ai-engineer:goal-crafter`"
  - "The trigger eval (`evals/measure_triggers.py`) scores no lower than before the move"
---

# Migrate to r0nny8000/claude-plugins

## Goal

Turn this single-plugin repo into a multi-plugin marketplace:

| Layer       | Today                          | Target                     |
| ----------- | ------------------------------ | -------------------------- |
| Repo        | `r0nny8000/goal-definer-skill` | `r0nny8000/claude-plugins` |
| Marketplace | `goal-definer-marketplace`     | `r0nny8000-plugins`        |
| Plugin      | `goal-definer`                 | `ai-engineer`              |
| Skill       | `goal-definer`                 | `goal-crafter`             |
| Skill call  | `/goal-definer:goal-definer`   | `/ai-engineer:goal-crafter` |

The plugin and marketplace names become part of every install id, and the
docs say to treat them as permanent. That is why this happens now, right
after the repo went public and before people install it.

## Decisions

| ID | Question                         | Decision                                                             |
| -- | -------------------------------- | -------------------------------------------------------------------- |
| D1 | Marketplace `name`               | `r0nny8000-plugins` (decided); plain `claude-plugins` is close to the reserved official names |
| D2 | Rename this repo or start fresh  | Rename on GitHub (decided): keeps history and ADRs, GitHub redirects the old URL |
| D3 | Plugin starting version          | `0.1.0` (proposed): new plugin name, nothing to be compatible with   |

D2 facts (docs.github.com, "Renaming a repository"): after a rename, `git
clone`, `git fetch` and `git push` on the old location keep working, unless a
new repo is later created under the old name.

## Target tree

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json            one entry: ai-engineer → ./plugins/ai-engineer
├── plugins/
│   └── ai-engineer/
│       ├── .claude-plugin/
│       │   └── plugin.json         name ai-engineer, version 0.1.0
│       ├── scripts/
│       │   ├── validate_goal.py
│       │   └── validate_goal.sh
│       ├── skills/
│       │   └── goal-crafter/
│       │       ├── SKILL.md
│       │       └── references/
│       └── README.md
├── tests/                          outside plugins/, so it isn't shipped
├── evals/
├── docs/adr/
├── docs/backlog/
├── LICENSE
├── pyproject.toml
└── README.md                       marketplace overview, install commands
```

`scripts/` sits at the plugin root, not inside the skill, so
`${CLAUDE_PLUGIN_ROOT}/scripts/validate_goal.sh` in `SKILL.md` keeps working
unchanged, and later skills in the plugin can share it.

## Files to change

| File                                         | Change                                                         |
| -------------------------------------------- | -------------------------------------------------------------- |
| `.claude-plugin/marketplace.json`            | Name `r0nny8000-plugins`, entry `ai-engineer`, source `./plugins/ai-engineer`    |
| `.claude-plugin/plugin.json`                 | Move to `plugins/ai-engineer/.claude-plugin/`, name `ai-engineer` |
| `scripts/*`                                  | `git mv` to `plugins/ai-engineer/scripts/`                     |
| `skills/goal-definer/`                       | `git mv` to `plugins/ai-engineer/skills/goal-crafter/`         |
| `SKILL.md`                                   | `name: goal-crafter`, H1 title; keep `description` plain (it drives triggering) |
| `tests/test_validate_goal*.py`               | Script paths → `plugins/ai-engineer/scripts/`                  |
| `evals/evals.json`                           | `skill_name` / `skill` → `goal-crafter`                        |
| `evals/measure_triggers.py`                  | Match `goal-crafter` instead of `goal-definer`                 |
| `evals/trigger-goal-definer.json`            | Rename to `trigger-goal-crafter.json`                           |
| `pyproject.toml`                             | `name = "claude-plugins"`                                      |
| `README.md`                                  | Root: marketplace overview and install; plugin README: goal-crafter usage, Claude Code only, Minecraft crafting framing |
| `docs/adr/0003-multi-plugin-marketplace.md`  | New ADR: why one marketplace repo, why rename over a fresh repo, the names |

`docs/plan.md` and ADRs 0001/0002 stay as history.

## Steps

1. Test first: update the test paths to `plugins/ai-engineer/scripts/` and
   watch them fail.
2. `git mv` the plugin manifest, scripts and skill; edit names. Tests go green.
3. Update evals, `pyproject.toml`, READMEs; write ADR 0003.
4. Run `claude plugin validate` on the marketplace and the plugin.
5. Commit, then rename the GitHub repo to `claude-plugins` and run
   `git remote set-url origin https://github.com/r0nny8000/claude-plugins.git`.
6. Push.
7. Switch your own machine over: remove the old `goal-definer-marketplace`
   registration, rename the local folder if wanted, add the new marketplace
   from the local path, install `ai-engineer@r0nny8000-plugins`.
8. Clean-environment check: add from GitHub, install, confirm
   `/ai-engineer:goal-crafter` appears; delete the stale cache at
   `~/.claude/plugins/cache/goal-definer-marketplace/`.
9. Run the trigger eval and compare with the earlier score.

## Risks

| Risk                                                         | Mitigation                                                    |
| ------------------------------------------------------------ | ------------------------------------------------------------- |
| Anyone who already installed `goal-definer@goal-definer-marketplace` loses it; `renames` only works inside one marketplace name | Repo just went public; README note with the new install commands |
| Unknown: what `marketplace update` does when the fetched `marketplace.json` has a new `name` | Users re-add instead of updating; tell them in the README     |
| Renaming the local folder breaks the `directory` marketplace in `~/.claude/settings.json` | Step 7 re-registers it                                        |
| Skill rename lowers auto-triggering                          | `description` unchanged; step 9 measures it                   |

## Checklist

- [x] D1, D2 decided
- [ ] D3 confirmed
- [ ] Test paths updated, tests fail
- [ ] Files moved and renamed, tests pass
- [ ] Evals, pyproject, READMEs, ADR 0003 updated
- [ ] `claude plugin validate` passes for marketplace and plugin
- [ ] Repo renamed on GitHub, remote updated, pushed
- [ ] Local machine switched to the new marketplace
- [ ] Clean install from GitHub shows `/ai-engineer:goal-crafter`
- [ ] Trigger eval score no lower than before
