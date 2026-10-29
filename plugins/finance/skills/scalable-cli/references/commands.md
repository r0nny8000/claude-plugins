# sc read commands

Read-only commands this skill may run, from the upstream command reference
(https://github.com/ScalableCapital/scalable-cli/blob/main/public-docs/commands.md).
Add `--json` for structured output; run `sc <command> --help` for all flags.

## Identity and session

| Task                       | Command                  |
|----------------------------|--------------------------|
| Check identity             | `sc whoami`              |
| Installed command surface  | `sc capabilities --json` |
| Show saved portfolio       | `sc broker context show` |
| List accessible portfolios | `sc broker portfolios`   |

Broker commands use the saved portfolio, or the only one if there is one.
When `sc broker portfolios` reports `selection_required`, ask the user which
portfolio to use. `sc broker context select --portfolio-id <ID>` saves that
choice locally; run it only after the user picked the portfolio. Never pick
one yourself.

## Portfolio and market data

| Task                          | Command                                                                            |
|-------------------------------|------------------------------------------------------------------------------------|
| Portfolio overview            | `sc broker overview --json`                                                        |
| Holdings                      | `sc broker holdings --json`                                                        |
| Cash, buying power, credit    | `sc broker cash-breakdown --json`                                                  |
| Transactions                  | `sc broker transactions --json`                                                    |
| One transaction               | `sc broker transaction details --transaction-id <ID> --json`                       |
| Portfolio value history       | `sc broker chart --timeframe 1y --json`                                            |
| Security price history        | `sc broker chart --isin <ISIN> --timeframe 1m --json`                              |
| Search a security             | `sc broker search "apple" --json`                                                  |
| Quote                         | `sc broker quote --isin <ISIN> --json`                                             |
| Security news                 | `sc broker security-news --isin <ISIN> --locale en_DE`                             |
| Derivatives on an underlying  | `sc broker derivatives search --underlying <ISIN> --type knockout --strategy long` |
| Trading venues                | `sc broker order-venues`                                                           |
| Portfolio groups              | `sc broker portfolio-groups`                                                       |
| Watchlist                     | `sc broker watchlist`                                                              |
| Price alerts                  | `sc broker price-alerts --active-only`                                             |
| Savings plans                 | `sc broker savings-plans`                                                          |
| Savings-plan options for ISIN | `sc broker savings-plans config --isin <ISIN>`                                     |
| Overnight savings             | `sc overnight`                                                                     |
| Overnight transactions        | `sc overnight transactions --json`                                                 |
| Fixed-Term accounts           | `sc fixed-term list --json`                                                        |
| One Fixed-Term account        | `sc fixed-term details --fixed-term-account-id <ID> --json`                        |

Chart timeframes: `1d`, `7d`, `1m`, `3m`, `6m`, `ytd`, `1y`, `max`.

## Reading the output

- Unavailable values are `null`; don't report them as zero.
- `sc broker overview` gives absolute returns per timeframe, not percentages.
  Don't present a calculated percentage as if sc returned it.
- Holdings and transactions keep securities in `items` and crypto in
  `crypto_items` / `crypto.items`; page with `--cursor` / `--crypto-cursor`.
- Transaction documents aren't available in the CLI; they're in the Scalable
  app. `sc broker analytics` is unavailable in this version.

## Errors

| Result                          | Meaning and next step                                    |
|---------------------------------|----------------------------------------------------------|
| `refresh_retryable`, exit 30    | Temporary; retry the same command once                   |
| `rate_limited`                  | Wait, respect any retry delay in the message, then retry |
| Login required                  | Ask the user to run `sc login` themselves                |
| `broker_chart_data_unavailable` | No series for that timeframe; try another                |
