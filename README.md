# claude-plugins

A Claude Code plugin marketplace by r0nny8000: one repo, several plugins, each
with its own skills and version.

## Plugins

| Plugin                              | Skills       | What it does                                                                                   |
|-------------------------------------|--------------|------------------------------------------------------------------------------------------------|
| [ai-engineer](plugins/ai-engineer/) | goal-crafter | Crafts strong `/goal` conditions from an interview and writes them as backlog files            |
| [finance](plugins/finance/)         | scalable-cli | Read-only helper for the Scalable Capital broker CLI `sc`: checks the install, reads the depot |

The plugins target Claude Code: the terminal, the IDE extensions, and the
desktop app's Code tab. They are not meant for claude.ai chat.

## Install

Without a GitHub SSH key in `ssh-agent`, tell Claude Code to clone over HTTPS:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1    # add to your shell profile
```

Add the marketplace once, then install a plugin:

```bash
claude plugin marketplace add r0nny8000/claude-plugins
claude plugin install ai-engineer@r0nny8000-plugins
```

Or both in one step inside a session (Claude Code 2.1.275 or later):

```text
/plugin install ai-engineer --marketplace r0nny8000/claude-plugins
```

Get new versions with `claude plugin update ai-engineer@r0nny8000-plugins`.

### Moving from goal-definer

This repo used to be `r0nny8000/goal-definer-skill`, with the plugin
`goal-definer@goal-definer-marketplace`. That install doesn't migrate on its
own. Replace it:

```bash
claude plugin marketplace remove goal-definer-marketplace
claude plugin marketplace add r0nny8000/claude-plugins
claude plugin install ai-engineer@r0nny8000-plugins
```

The skill is now `/ai-engineer:goal-crafter`.

### From a local clone

Load a plugin for one session while developing:

```bash
claude --plugin-dir /path/to/claude-plugins/plugins/ai-engineer
```

Or add the clone as a local marketplace. It then loads your current files at
every session start:

```bash
claude plugin marketplace add /path/to/claude-plugins
claude plugin install ai-engineer@r0nny8000-plugins
```

## Layout

```
.claude-plugin/marketplace.json   the catalog: one entry per plugin
plugins/<plugin>/                 what users install; only this folder is copied
  .claude-plugin/plugin.json      name and version
  skills/<skill>/SKILL.md
  scripts/
tests/, evals/, docs/             development only, not shipped
```

Decisions are in [docs/adr/](docs/adr/), open work in `docs/backlog/`.

## Develop

```bash
uv run pytest                                      # validator and check-script tests
claude plugin validate --strict .                  # marketplace
claude plugin validate --strict plugins/ai-engineer
claude plugin validate --strict plugins/finance
```

To release a plugin, bump `version` in its `.claude-plugin/plugin.json`.
GitHub installs stay on their cached copy until that string changes.

Skill evals (skill-creator method) live in `evals/`: `evals.json` holds the
test prompts, `make_fixture.sh` builds the sample repo, `grade.py` scores an
iteration, `measure_triggers.py` checks signal-word triggering of the
installed plugin against `trigger-goal-crafter.json`:

```bash
uv run python evals/measure_triggers.py evals/trigger-goal-crafter.json claude-opus-5-5 /tmp/goal-crafter.json
```

For the uninstalled finance plugin, name the skill and the plugin folder.
`check_install_guidance.py` runs one session on a machine without `sc` and
passes when Claude shows the install steps without running them:

```bash
uv run python evals/measure_triggers.py evals/trigger-scalable-cli.json claude-opus-5-5 /tmp/scalable-cli.json \
  --skill scalable-cli --plugin-dir plugins/finance
uv run python evals/check_install_guidance.py
```

Test sessions run with `ENABLE_CLAUDEAI_MCP_SERVERS=false` and
`--strict-mcp-config`, so a claude.ai connector can't answer instead of the
skill.

## License

MIT, see [LICENSE](LICENSE).
