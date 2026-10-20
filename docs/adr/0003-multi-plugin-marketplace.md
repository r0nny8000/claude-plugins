# 0003 Multi-plugin marketplace repo: claude-plugins, ai-engineer, goal-crafter

Status: accepted
Date: 2026-10-20

## Context

The repo was a single plugin and its own marketplace: `marketplace.json` and
`plugin.json` side by side in `.claude-plugin/`, entry `"source": "./"`. The
user wants more plugins, each with more than one skill, all in one repo.

With `"source": "./"` the whole repo is the plugin, so Claude Code copies
everything into the user's cache, including `tests/`, `evals/` and `docs/`
(seen in `~/.claude/plugins/cache/goal-definer-marketplace/goal-definer/0.1.0`).
A second plugin in a subfolder would ship inside the first one.

The marketplace name and the plugin name form the install id
(`<plugin>@<marketplace>`), and the Claude Code docs say to treat a plugin
name as permanent. The repo had just gone public, so this was the cheapest
moment to rename.

## Alternatives

| Option                                                     | Verdict  | Reason                                                                                      |
|------------------------------------------------------------|----------|---------------------------------------------------------------------------------------------|
| Keep one plugin per repo, a separate catalog repo pointing at each | rejected | One repo per plugin is more to maintain for one author                               |
| One repo, plugins under `plugins/<name>/`                  | chosen   | The layout of the docs' multi-plugin walkthrough; only the plugin folder ships               |
| New repo `claude-plugins`, archive `goal-definer-skill`    | rejected | Loses history and ADRs in the active repo                                                   |
| Rename `goal-definer-skill` to `claude-plugins` on GitHub  | chosen   | Keeps history; GitHub redirects clone and fetch from the old URL                            |

## Decision

- Repo `r0nny8000/claude-plugins`, marketplace name `r0nny8000-plugins`.
  Plain `claude-plugins` was avoided because it sits close to the reserved
  official names such as `claude-plugins-official`.
- First plugin `ai-engineer` at `plugins/ai-engineer/`, version `0.1.0`.
- The skill `goal-definer` becomes `goal-crafter`, called
  `/ai-engineer:goal-crafter`. The name borrows Minecraft's crafting table:
  the interview collects the ingredients, the template arranges them. The
  crafting framing stays in the README; the skill's `description` keeps its
  plain wording because it drives automatic triggering.
- Shared plugin scripts live at the plugin root (`plugins/ai-engineer/scripts/`),
  so `${CLAUDE_PLUGIN_ROOT}/scripts/...` works for every skill in the plugin.
- `tests/`, `evals/` and `docs/` stay at the repo root and are not shipped.

## Consequences

- Existing installs of `goal-definer@goal-definer-marketplace` don't migrate:
  a `renames` map only works inside one marketplace name. The README tells
  users to remove the old marketplace and install `ai-engineer@r0nny8000-plugins`.
- Each plugin is versioned on its own; all skills in a plugin share its
  version.
- The GitHub redirect from `goal-definer-skill` breaks if a new repo is ever
  created under that name.
