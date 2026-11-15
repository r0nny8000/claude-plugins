---
name: scalable-cli
description: Read-only helper for the Scalable CLI `sc`, the official command line of the Scalable Capital broker. Checks whether sc is installed, current and logged in, shows the install steps for the user's OS, and runs sc read commands for the Scalable depot or portfolio - holdings, overview, cash, transactions, quotes, savings plans, Overnight and Fixed-Term savings. Use it whenever the user mentions Scalable, Scalable Capital, their Scalable depot, portfolio or broker account, or the sc CLI; whenever they want to buy or sell a stock, ETF or other security (it can't trade, so it says so and points to the Scalable app); and whenever they want a quote, price or other data for a stock or ETF, for example by ISIN - even if they don't say "skill" or name Scalable. It never logs in, trades or changes savings plans.
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

| Finding               | What to tell the user                                                                                                                                                                               |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `not_installed`       | Fetch the current upstream steps as [install.md](references/install.md) says and show the ones for their `system` and `machine`; they run them, you don't                                           |
| `update_available`    | Name installed and latest version. For a data request, say so in one line and go on; fetch and show upstream's update steps as install.md says only when the user asks about installing or updating |
| `not_logged_in`       | First enable Agentic Investing on the Scalable web platform (Profile > Security), then run `sc login` yourself in your own terminal, not through Claude                                             |
| `refresh_retryable`   | Temporary session refresh error; run the check once more                                                                                                                                            |

After showing install or update steps, ask the user (with AskUserQuestion
when available) whether you should write a one-time install script they run
and that deletes itself afterwards. If they say yes, or asked for one,
follow [install-script.md](references/install-script.md). Never run it.

With an empty `findings` list, sc is ready. A user who only asked whether sc
is installed gets the answer and, if it's missing, the install steps and
the script offer; stop there.

## 2. Read data

These three commands are known to work. Run them directly, without
`sc capabilities` or help first:

| Request                                   | Command                           |
|-------------------------------------------|-----------------------------------|
| Portfolio value, performance, overview    | `sc broker overview --json`       |
| Cash, buying power                        | `sc broker cash-breakdown --json` |
| Positions, holdings                       | `sc broker holdings --json`       |

For any other request, compose the command from `sc`'s help as section 3
describes. If a listed command is unknown to the installed `sc` (missing
from `sc capabilities --json` or its help), find the current one through
help as well and tell the user the skill's list is out of date.

Answer in plain language, keep `null` values as unavailable rather than
zero, and don't invent percentages sc didn't return. If several portfolios
exist, ask the user which one; never pick one yourself. Portfolio
selection, output and errors are in [commands.md](references/commands.md).

## 3. Getting help

For a request the list doesn't cover, the installed `sc`'s built-in help is
always the first step; it describes exactly the version the user has.

| Form                                 | Shows                                                                                                      |
|--------------------------------------|------------------------------------------------------------------------------------------------------------|
| `sc --help` or `sc -h`               | Top-level commands                                                                                         |
| `sc help <command>`                  | Help for a command or subcommand, for example `sc help broker` or `sc help broker quote`                   |
| `sc <command> --help` or `-h`        | Usage and every option with accepted values and defaults, for example `sc broker quote --help`             |
| `sc capabilities --json`             | Every command as a dotted name (`broker.quote` is `sc broker quote`), exit codes and multi-step workflows  |

Options have no help of their own: each option is explained in its
command's help, with its accepted values and default.

From request to command:

1. Find the command in `sc capabilities --json` or in a parent's help, for
   example `sc broker --help`.
2. Read that command's `--help` for its flags.
3. Compose the command with `--json`, check [safety.md](references/safety.md)
   that it only reads, then run it.

Fallback only when that help doesn't answer the request: fetch the upstream
manual from the `main` branch,
https://github.com/ScalableCapital/scalable-cli/blob/main/public-docs/commands.md,
never a copy. If the fetch fails, say so, give the link, and stop without
running a guessed command.

## 4. Stay read-only

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
