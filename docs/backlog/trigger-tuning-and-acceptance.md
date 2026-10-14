---
status: open
priority: high
acceptance: >
  Both skills trigger on at least 7 of 10 should-trigger prompts in
  evals/trigger-*.json with no false triggers; the live end-to-end test
  (definer interview -> fresh session -> goal-runner -> pasted /goal starts
  and is evaluated) passes; plugin installed from the local marketplace.
---

# Trigger tuning and live acceptance

State on 2026-10-13:

- Iteration 2 evals: 100% with skill vs 57% without (scratchpad workspace).
- Trigger measurement with the current descriptions: goal-definer 1/10,
  goal-runner 0/8 on the should-trigger prompts (threshold 2 of 3 runs);
  0 false triggers. The harness runs in an empty dir without NEXTGOAL.md.
- skill-creator `run_loop` failed: its description-improvement step got
  `claude -p exited 1` with empty stderr. Debug that (run the improve call
  manually) or rewrite the descriptions by hand and re-measure with
  `run_eval`.
- 2026-10-14: root cause verified. The improve call's stdout reads "You've
  hit your session limit"; skill-creator's `_call_claude` only prints stderr,
  hence the empty error. Not a bug in the skills. Rerun after the limit
  resets, using the wrapper that prints stdout (scratchpad
  `trigger/loop_debug.py`; recreate it if the scratchpad is gone).

Remaining steps from docs/plan.md: 6b (tuning), 7 (install via
`claude plugin marketplace add` + `claude plugin install`), 8 (live acceptance).
