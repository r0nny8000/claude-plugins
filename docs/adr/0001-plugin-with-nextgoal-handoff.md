# 0001 Plugin with NEXTGOAL.md handoff to a fresh session

Status: superseded in part by 0002 (goal-runner and NEXTGOAL.md were dropped)
Date: 2026-10-13

## Context

`/goal <condition>` keeps Claude working until a separate evaluator judges the
condition met. The evaluator is a small fast model that sees only the
condition text and the transcript. It runs no tools and reads no files. The
condition is capped at 4,000 characters (code.claude.com/docs/en/goal).

Anthropic's best practices recommend: interview the user with
AskUserQuestion, write a spec, then execute it in a fresh session with clean
context (code.claude.com/docs/en/best-practices).

We want a skill that runs that interview and hands a well-formed goal to a
fresh session.

## Alternatives

| Option                                  | Verdict  | Reason                                                                                                       |
|-----------------------------------------|----------|--------------------------------------------------------------------------------------------------------------|
| `/goal @NEXTGOAL.md`                    | rejected | Undocumented; the evaluator sees the literal condition, so a file reference may never reach it               |
| Shell launcher `claude "/goal ..."`     | rejected | Unverified whether interactive argv runs slash commands; adds a script outside Claude Code                  |
| Skill runs /goal itself                 | rejected | Built-in commands like /goal are not available through the Skill tool                                        |
| Interview inside a forked subagent      | rejected | Subagents don't see the conversation and cannot use AskUserQuestion                                          |
| NEXTGOAL.md + goal-runner skill         | chosen   | goal-runner loads the brief into the transcript, confirms, and prints the exact /goal line for the user      |

Packaging: a plugin (user's choice) over a symlinked personal skill, so both
skills and the validator ship as one installable unit.

## Decision

- Plugin `goal-definer` with two skills: `goal-definer` (interview, writes
  NEXTGOAL.md) and `goal-runner` (fresh session: validate, confirm, print the
  /goal line).
- Codebase research runs in an Explore subagent; the interview stays in the
  main session.
- NEXTGOAL.md is a gitignored temporary file, deleted after the goal is met.
- Both skills trigger by command and by signal words.
- `scripts/validate_goal.py` checks NEXTGOAL.md deterministically.

## Consequences

- The user pastes one /goal line in the new session; full automation is not
  possible with current Claude Code.
- Plugin skills are namespaced (`/goal-definer:goal-runner`).
- The skill must be revisited when /goal changes; facts carry a verified date.
