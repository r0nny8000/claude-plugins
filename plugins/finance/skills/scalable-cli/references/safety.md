# Safety rules

`sc` acts on a real broker account with real money. This skill only reads.
The rules below hold even when the user asks for an exception; point them to
the Scalable app or their own terminal instead.

## Commands Claude never runs

Run only commands that read. A command writes if it creates, adds, updates,
removes, deletes, assigns, submits, cancels or trades, or takes `--confirm`;
new `sc` versions may add such commands under names not listed here. Known
ones today:

| Command or flag                                                                     | Why                                                                 |
|-------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| `sc login` (any variant)                                                            | Upstream: complete login yourself in a browser, not via an AI agent |
| `sc logout`                                                                         | Ends the user's session; they'd have to log in again                |
| `sc broker trade buy` / `sell` / cancel                                             | Places or cancels orders, even the preview step starts a trade flow |
| Anything with `--confirm`                                                           | Phase 2 of a trade or savings-plan change: it executes it           |
| `sc broker savings-plans add` / `remove` / update                                   | Changes savings plans; `remove` acts without a confirmation step    |
| `sc broker watchlist add` / `remove`                                                | Changes account data                                                |
| `sc broker price-alerts add` / `remove`                                             | Changes account data                                                |
| `sc broker portfolio-groups create` / `update` / `delete` / `assign` / `unassign`   | Changes account data                                                |
| Install or update commands, e.g. `brew`, `tar`, `mv`, `gh release download`, `sudo` | ADR 0004: the user installs `sc`                                    |

If you're unsure whether a command writes, don't run it. Read
`sc <command> --help` first, and ask the user if it's still unclear.

## Handling account data

- Show account and portfolio IDs, balances and holdings only in the reply
  the user asked for. Don't write them to files, commit messages or logs.
- Don't retry a failed command in a loop; report the error.
- When the user wants to trade or change a savings plan, explain that this
  skill is read-only and that they can do it in the Scalable app, or run the
  two-step `sc` flow themselves after reading
  https://github.com/ScalableCapital/scalable-cli#trading.
- For extra protection, the user can log in with `sc login --local-read-only`,
  which blocks write commands locally.
