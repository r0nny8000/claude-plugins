---
name: scalable-cli
description: Read-only helper for the Scalable CLI `sc`, the official command line of the Scalable Capital broker. Checks whether sc is installed, current and logged in, shows the install steps for the user's OS, and runs sc read commands for the Scalable depot or portfolio - holdings, overview, cash, transactions, quotes, savings plans, Overnight and Fixed-Term savings. Use it whenever the user mentions Scalable, Scalable Capital, their Scalable depot, portfolio or broker account, or the sc CLI, even if they don't say "skill". It never logs in, trades or changes savings plans.
---

# Scalable CLI (read-only)

Helps the user with the Scalable CLI `sc` without changing their account.
`sc` acts on a real broker account, so this skill reads and guides; the user
runs anything that installs, logs in or moves money.

## 1. Check sc first

Run the check script before any `sc` command, with the skill's base directory
(shown when the skill loads) in place of `<skill-dir>`:

```bash
python -I <skill-dir>/scripts/check_install.py
```

It prints JSON with `system`, `machine`, `libc`, `version`, `latest_version`
and `findings`. It never prints `sc` output, so no account data shows up.
Handle each finding before going on:

| Finding             | What to tell the user                                                                                                                                     |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| `not_installed`     | Fetch the current upstream steps as [install.md](references/install.md) says and show the ones for their `system` and `machine`; they run them, you don't |
| `update_available`  | Name installed and latest version; fetch and show upstream's update steps as install.md says                                                              |
| `not_logged_in`     | First enable Agentic Investing on the Scalable web platform (Profile > Security), then run `sc login` yourself in your own terminal, not through Claude   |
| `refresh_retryable` | Temporary session refresh error; run the check once more                                                                                                  |

With an empty `findings` list, sc is ready. A user who only asked whether sc
is installed gets the answer and, if it's missing, the install steps; stop
there.

## 2. Read data

Find the read command from the installed `sc` itself
(`sc capabilities --json`, `sc <command> --help`) as
[commands.md](references/commands.md) describes, and add `--json`. Answer in
plain language, keep `null` values as unavailable rather than zero, and don't
invent percentages sc didn't return. If several portfolios exist, ask the
user which one; never pick one yourself.

## 3. Stay read-only

The known write commands and the reasons are in [safety.md](references/safety.md). In short:

- Never run `sc login` or `sc logout`; the user logs in in their own terminal.
- Never run `sc broker trade` commands or place, preview or cancel a trade.
- Never create, change or remove a savings plan (`sc broker savings-plans add` / `remove`).
- Never pass `--confirm`; it executes trades and savings plan changes.
- Never change watchlists, price alerts or portfolio groups, or run any other command that writes.
- Never run install or update commands (`sudo`, `brew`, `tar`, `mv`, `gh release download`); show them for the user to run.

When the user wants a trade or a savings plan change, explain the skill is
read-only and point them to the Scalable app or the upstream Trading section:
https://github.com/ScalableCapital/scalable-cli#trading.

More background and doc links are in [README.md](README.md).
