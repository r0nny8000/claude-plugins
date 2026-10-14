# /goal best practices

Verified against official docs on 2026-10-13 (Claude Code 2.1.296). Re-check
code.claude.com/docs/en/goal when /goal behaves differently than described.

## How /goal works (official)

| Fact                                                                                       | What it means for a goal                                                     |
|--------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| After each turn a small fast model judges the condition against the transcript              | Write conditions the transcript can prove                                     |
| The evaluator runs no tools and reads no files                                              | Each check must be a command whose output Claude prints                       |
| Verdicts: not yet met (keep going, reason becomes guidance), met, impossible                | A vague condition either never clears or clears at a random point             |
| No tool use for several turns in a row stops the loop, goal stays set                       | Give Claude concrete work to do, not something to argue about                 |
| Condition max 4,000 characters                                                              | Compact condition; details go in the brief                                    |
| A turn or time clause ("or stop after 20 turns") bounds the run                             | Always include one                                                            |
| /goal does not change the permission mode                                                   | Unattended runs need auto mode or pre-allowed commands                        |
| `/clear` removes the goal; resume restores it with counters reset                           | Execute in a fresh session; don't /clear mid-goal                              |
| Unavailable when hooks are disabled or the folder is untrusted                              | Tell the user if /goal refuses                                                |
| Setting a goal starts a turn immediately with the condition as directive                    | The condition doubles as the first prompt: make it readable as an instruction |

Recommended shape (official): one measurable end state, a stated check, and
constraints that matter.

Good fits (official): migrate a module until every call site compiles and tests
pass; implement a design doc until all acceptance criteria hold; split a file
until each module is under a size budget; work a labeled backlog until empty.

## Do

- One measurable end state: test result, exit code, file count, empty queue.
- Name the exact command that proves each criterion (`uv run pytest` exits 0).
- Ask Claude to show each check's output in the transcript, so the evaluator
  sees evidence rather than claims.
- Guard test integrity: no test deleted, skipped, or weakened.
- Bound the blast radius: which paths may change, which must not.
- State what is out of scope.
- Add a stop clause and ask for a report of what remains.
- Start on a clean tree and a feature branch; review the diff afterwards.
- Validate before you write: run the test command once, confirm files exist,
  check external API behavior in docs.

## Don't

- Subjective end states: better, cleaner, nicer, more readable.
- Dependencies outside your control: production APIs, flaky external services.
  Use local or staging checks.
- Conditions that need a human verdict ("the UI looks right") unless Claude
  can produce comparable evidence (screenshot diff).
- Single-turn fixes; /goal adds overhead without benefit.
- Work that needs approval of each change, or irreversible actions
  (deploys, data deletion, pushing to main).
- Step-by-step instructions as the condition. State outcomes; keep hints short.

## Sources

- Official: https://code.claude.com/docs/en/goal
- Official: https://code.claude.com/docs/en/best-practices (verification,
  interview with AskUserQuestion, spec then fresh session)
- Community: https://inventivehq.com/blog/claude-code-goal-command-guide
- Community: https://www.mindstudio.ai/blog/claude-code-goal-command-autonomous-agents
- Community: https://findskill.ai/blog/claude-code-goal-command/
- Community: https://amitray.com/claude-code-goal-command-guide-2026/
