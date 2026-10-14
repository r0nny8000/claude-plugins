# Interview rounds

Every round follows the same loop, so the user always knows what's coming:

1. Draft: propose the section from recon facts and earlier answers.
2. Ask: one AskUserQuestion call, up to 4 questions, 2-4 options each.
   Put the recommended option first with "(Recommended)". Use multiSelect
   when choices combine (guardrails, out-of-scope items).
3. Show: a short table of the section as it now stands.
4. Check: does the section meet its quality bar? If not, run one more round
   on the gap only.

Skip a question when recon or earlier answers already settle it; say what you
assumed instead. The user should mostly pick, rarely type.

## Rounds in order

| Round                | Ask about                                                                    | Quality bar                                                         |
|----------------------|------------------------------------------------------------------------------|---------------------------------------------------------------------|
| 1 Goal               | The outcome in one sentence; which of 2-3 framings fits                      | Outcome, not steps; one end state                                   |
| 2 Acceptance         | Which criteria define done; which command proves each                        | Every item has a command and expected result                        |
| 3 Verification       | The final end-to-end check; whether it was run once successfully already     | Command exists and runs today (you validated it)                    |
| 4 Guardrails         | Paths allowed to change, invariants (public API, deps, migrations, git ops)  | Includes test integrity; blast radius stated                        |
| 5 Out of scope       | Adjacent work that is tempting but excluded                                  | At least one concrete item, or an explicit "nothing adjacent"       |
| 6 Budget and mode    | Turn or time cap; permission mode for the run; branch                        | Stop clause present; user knows auto mode is needed for unattended  |

## Question patterns

Prefer concrete options drawn from recon over open questions:

- "Which test command proves this?" options: the commands you found in
  pyproject.toml, package.json, Makefile, or CI config.
- "Which paths may change?" multiSelect: directories touched by the task.
- "Which invariants must hold?" multiSelect: no public API change, no new
  dependencies, no migration edits, no git push, no changes to CI config.
- "Turn budget?" options sized to the task: 10 (small), 25 (medium),
  50 (large), plus time-based.

## Red flags to probe

| Signal in the answer                         | Follow-up                                                       |
|----------------------------------------------|-----------------------------------------------------------------|
| Subjective word (better, clean, faster)      | "Which measurement shows it?" offer metrics or commands         |
| External system in the check                 | Offer a local or staging alternative                            |
| No existing tests                            | Offer: write the tests first as part of the goal, with a guard  |
| Dirty tree or on main                        | Offer to commit/stash or create a branch before handoff         |
| Several unrelated outcomes                   | Offer to split into separate goals; keep one in NEXTGOAL.md     |
| Irreversible action (deploy, push, delete)   | Move to out of scope; the user does it after review             |
