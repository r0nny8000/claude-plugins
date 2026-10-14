---
status: goal-ready
priority: medium
acceptance: ~/research/amd-cpu-under-300.md names the fastest gaming AM5 Ryzen under 300 EUR; `python ~/research/check_cpu_report.py ~/research/amd-cpu-under-300.md` exits 0
---

# Goal: Fastest AM5 gaming CPU under 300 EUR

## Goal

Identify the AM5 desktop Ryzen CPU with the highest gaming performance whose
lowest new price on Geizhals.de is below 300 EUR on the day of the run.

## Context

- Repo state: goal-definer-skill repo, branch main, clean tree. The repo is
  only where this goal file lives; the research output goes to `~/research/`.
- Relevant files: none in this repo. Output: `~/research/amd-cpu-under-300.md`
  (report) and `~/research/check_cpu_report.py` (check script), both new.
- Decisions to respect: user's CLAUDE.md (Python via `python`, tables
  column-aligned, no bold in Markdown).
- Verified facts: no tests or code involved; this is web research. Prices
  change daily, so the report states the check date.
- Files left by validation runs: none.

## Acceptance checklist

- [ ] Report lists every AM5 desktop Ryzen (boxed or tray, new) with a lowest Geizhals.de price below 300 EUR, at least 3 rows — proven by `python ~/research/check_cpu_report.py ~/research/amd-cpu-under-300.md` reporting the row count
- [ ] Each row has model, cores/threads, price in EUR, price check date, geizhals.de link, gaming index, and index source — proven by the same script exiting 0
- [ ] All gaming indices come from one review that tests every listed CPU (ComputerBase, PCGH, or TechPowerUp); the source URL is in the report — proven by the script checking that one source is shared by all rows
- [ ] A `Winner:` line names the row with the highest gaming index, and a second review is cited that confirms the winner's rank among the candidates — proven by the script checking that the winner matches the maximum and that a `Cross-check:` line with a URL exists

## Verification

Run `python ~/research/check_cpu_report.py ~/research/amd-cpu-under-300.md`.
It must exit 0 and print the row count, the price range, and the winner. Then
run `cat ~/research/amd-cpu-under-300.md`. Show both outputs in the
transcript.

## Guardrails

- No test is deleted, skipped, or weakened to make a check pass: the script
  must actually parse the report and fail on a price at or above 300, a
  missing link, or a winner that is not the maximum.
- No writes outside `~/research/`, except reading and, when done, offering to
  delete this goal file.
- Read-only web use: no accounts, carts, purchases, or form submissions.

## Out of scope

- Mainboard, RAM, or cooler recommendations.
- Intel CPUs and used CPUs.
- Buying anything; the user buys after review.
- Laptop and mobile/APU-only chips.

## Approach hints

- Geizhals.de CPU category filtered by socket AM5 and price gives the
  candidate list; X3D models near 300 EUR are the likely contenders.
- Choose the most recent gaming review that covers all candidates; record its
  relative performance (percent) as the index.

## When done

Ask the user whether to delete this file. Deleting is fine: it stays in git
history if it was committed.

## Open questions

None

## Condition

```text
~/research/amd-cpu-under-300.md names the AM5 desktop Ryzen with the highest gaming performance whose lowest new Geizhals.de price is below 300 EUR today, as shown by `python ~/research/check_cpu_report.py ~/research/amd-cpu-under-300.md` exiting 0. Checklist: (1) every AM5 desktop Ryzen under 300 EUR on Geizhals.de is listed, at least 3 rows; (2) each row has model, cores/threads, price in EUR, check date, geizhals.de link, gaming index, index source; (3) all indices come from one review (ComputerBase, PCGH or TechPowerUp) covering every listed CPU; (4) a Winner: line names the highest-index row and a Cross-check: line cites a second review with URL. The script must really parse the report and fail on price >= 300, a missing link, or a wrong winner. Guardrails: no test deleted, skipped or weakened; writes only in ~/research/ (plus reading and offering to delete docs/backlog/goal-amd-cpu-under-300.md); read-only web, no accounts, carts or purchases. Out of scope: mainboard/RAM/cooler advice, Intel, used CPUs, laptop chips, buying. Show the output of the check script and `cat` of the report in the transcript. Or stop after 20 turns and report what remains.
```
