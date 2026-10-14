---
status: open
priority: high
acceptance: >
  goal-definer triggers on at least 7 of 10 should-trigger prompts in
  evals/trigger-goal-definer.json with no false triggers.
---

# Trigger tuning and live acceptance

State on 2026-10-14:

- Skill evals (iteration 2, before goal-runner was removed): 100% with the
  skill vs 57% without.
- Trigger measurement with the original description: goal-definer 1/10 on
  the should-trigger prompts (threshold 2 of 3 runs), 0 false triggers. The
  harness runs in an empty dir. Description tuning has not run yet.
- skill-creator `run_loop` failed twice at the improve step. Root cause
  verified: the improve call's stdout reads "You've hit your session limit";
  skill-creator's `_call_claude` only prints stderr, hence the empty error.
  Not a bug in the skills. Rerun after the limit resets with a wrapper that
  prints stdout (recreate it if the scratchpad is gone).
- `/goal @file` was tested: `@` is not expanded inside `/goal` (ADR 0002),
  the "Read it first" wording makes the goal work anyway.

- Live acceptance on a real project passed (user, 2026-10-14): interview
  questions good, goal file stored under docs/backlog, pasted `/goal` line
  works.

Remaining:

1. Run the tuning loop for goal-definer and re-measure; apply the best
   description only if it scores higher on the held-out prompts.
