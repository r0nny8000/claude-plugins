# CLAUDE.md

## Plugin versioning

- When a change touches a plugin (its skills, scripts, or references), ask whether to bump that plugin's `version` in `plugins/<plugin>/.claude-plugin/plugin.json` — once while writing the plan, and again before committing. Ask with AskUserQuestion (patch / minor / major / no bump). Installed users only receive the update automatically when the version number changes.
