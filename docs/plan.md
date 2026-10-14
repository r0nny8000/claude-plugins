# Plan: goal-definer plugin (define + goal-runner)

## Context

`/goal <condition>` keeps Claude working until a separate evaluator judges the
condition met. Writing a condition that holds up across many turns is hard:
vague goals spin or stop early. You want a skill that interviews you
(AskUserQuestion), researches the project first, and writes a strong goal into
NEXTGOAL.md. A fresh session then picks it up and runs it.

Repo: /home/autobot/code/r0nny8000/goal-definer-skill. Git is initialized,
there are no commits yet, and the branch is `master`.

## Research findings (verified)

Official sources: code.claude.com/docs/en/goal, /best-practices, /skills, /plugins.
Facts that drive the design:

| Fact                                                                                 | Consequence for the skill                                                                                          |
|--------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| The evaluator (small fast model) sees only the condition and the transcript. It runs no tools and reads no files. | Every check must be a command whose output Claude prints. File contents count only once Claude has read them into the transcript. |
| The condition is capped at 4,000 chars                                               | NEXTGOAL.md has two parts: a full brief, and a compact condition of 4,000 chars or fewer.                          |
| Recommended shape: one measurable end state, a stated check, constraints             | These become the mandatory sections of the template.                                                               |
| A turn or time clause ("or stop after N turns") bounds the run                       | Every goal gets a stop clause.                                                                                     |
| Verdicts: not yet met, met, impossible. A stall (no tool use for several turns) stops the loop | Turn clause plus "report remaining work". Avoid conditions that can't converge.                            |
| `/clear` removes the goal. `--resume` restores it but resets the counters            | Fresh session for execution matches the docs ("start a fresh session to execute the spec").                     |
| /goal does not change the permission mode. Auto mode is needed for unattended runs  | goal-runner checks the mode and tells you.                                                                         |
| /goal is unavailable when hooks are disabled or the workspace is untrusted          | goal-runner mentions this if /goal refuses.                                                                        |
| Best practices: interview via AskUserQuestion, then write a spec, then a fresh session | This exactly matches your workflow idea.                                                                         |
| Good specs name files and interfaces, state what is out of scope, and end with an end-to-end verification | Template sections.                                                              |
| Skills can't run built-ins like /goal (only /init and /security-review are exposed)   | goal-runner prints the exact `/goal ...` line for you to paste. It can't run it itself.                           |
| Subagents (`context: fork`) don't see the conversation and can't ask the user        | The interview stays in the main session. Only the research goes to an Explore subagent.                           |
| Plugin skills are namespaced: `/goal-definer:goal-runner`                            | Bare `/goal-runner` is unverified. I'll check it in step 1.                                                        |

Community practice (secondhand; inventivehq, mindstudio, findskill, amitray):
- No subjective end states ("cleaner", "better").
- No dependencies on systems you don't control (prod APIs).
- Run on a branch and review the diff.
- Don't use /goal for single-turn fixes, per-change approval, irreversible
  actions, or a dirty working tree.
- Guard against reward hacking with "no test is deleted, skipped or weakened".

## Section evaluation for the goal brief

| Section                | Keep? | Why                                                                          |
|------------------------|-------|------------------------------------------------------------------------------|
| Goal / overall task    | yes   | One sentence, the outcome rather than the steps                              |
| Context (files, ADRs)  | yes   | Points to the sources so the fresh session doesn't re-explore                |
| Acceptance checklist   | yes   | Each item is verifiable and has the command that proves it                   |
| Verification (done)    | yes   | Final end-to-end check whose output must appear in the transcript            |
| Guardrails (must hold) | yes   | Invariants: no test weakening, no edits outside X, no public API change      |
| Out of scope / not-do  | yes   | Prevents sprawl. Merge "not to do" into this section                         |
| Stop clause / budget   | yes   | "or stop after N turns and report remaining work"                            |
| Approach / plan steps  | short | Hints only. /goal works best from outcomes, not instructions                 |
| Risks / open questions | yes   | Must be empty before handoff. Anything open becomes an interview question    |

## Architecture

```
goal-definer-skill/                    (repo = plugin + local marketplace)
├── .claude-plugin/plugin.json         name: goal-definer
├── .claude-plugin/marketplace.json    local marketplace for /plugin install
├── skills/goal-definer/SKILL.md       /goal-definer:goal-definer  (interview)
├── skills/goal-definer/references/
│   ├── best-practices.md              do/don't list, with sources
│   ├── interview.md                   the repeating question rounds
│   └── template.md                    NEXTGOAL.md template
├── skills/goal-runner/SKILL.md        /goal-definer:goal-runner (handoff)
├── scripts/validate_goal.py           deterministic NEXTGOAL.md checks
├── tests/test_validate_goal.py        pytest
├── docs/adr/0001-*.md                 handoff design decision
├── README.md, .gitignore (NEXTGOAL.md, .venv, __pycache__)
```

### Triggering
Both skills start either from their command or from signal words (Claude
loads them on its own via `description`; `disable-model-invocation` stays
unset).

| Skill        | Command                     | Signal words (in `description`)                                 |
|--------------|-----------------------------|-----------------------------------------------------------------|
| goal-definer | /goal-definer:goal-definer  | define a goal, write a /goal, prepare NEXTGOAL, goal condition  |
| goal-runner  | /goal-definer:goal-runner   | run the next goal, start NEXTGOAL, execute the goal             |

goal-runner always asks for confirmation before it prints the /goal line, so
a false trigger is harmless.

### Build method
Use the `anthropic-skills:skill-creator` skill to draft both skills, run its
eval cases (trigger and no-trigger prompts, plus a full interview run), and
tune the descriptions until the signal words trigger reliably.

### goal-definer flow (repeating interview structure)
1. Intake: take the task from `$ARGUMENTS`, or ask for it.
2. Recon (Explore subagent): git status, branch, recent log, README,
   CLAUDE.md, docs/adr, docs/backlog, test/lint commands, and code related to
   the task. It returns a short fact sheet. Optional web research when the task
   involves external APIs or libraries.
3. Validate: check what you claimed (file exists, test command runs, the API
   really behaves that way) before turning it into a criterion.
4. Interview rounds. The same loop runs for each section, in this order:
   Goal, Acceptance checklist, Verification, Guardrails, Out of scope, Budget.
   - Propose options pre-filled from recon so you mostly pick and rarely type.
   - Up to 4 questions per AskUserQuestion call, multiSelect where it fits.
   - After each round, show a short draft table of that section.
   - Move on once the section passes its quality bar (references/interview.md).
5. Lint: run `validate_goal.py`, fix findings, and confirm the condition is
   4,000 chars or fewer.
6. Write NEXTGOAL.md, show the condition, and tell you: "/clear or a new
   session, then /goal-definer:goal-runner".

### goal-runner flow
1. Read NEXTGOAL.md and stop with a hint if it's missing.
2. Run the validator. Check git state (clean tree, not on main) and permission
   mode.
3. Show a summary table and ask via AskUserQuestion: run / edit / abort.
4. Print the full brief into the transcript so the evaluator and Claude both
   see the context. Then print the exact `/goal <condition>` line to paste.
5. After the goal is met, a later invocation offers to delete NEXTGOAL.md.

### validate_goal.py (Python, run via `uv run`)
Checks:
- Required sections are present.
- The condition block is 4,000 chars or fewer.
- A stop clause exists.
- At least one check command in backticks.
- No subjective words (better, clean, nice, improve) inside the condition.
- The guardrails include a test-integrity rule.
- No open questions remain.

Exit code 0 or 1, with readable findings.

## Risks

| Risk                                                             | Mitigation                                                      | Level  |
|------------------------------------------------------------------|-----------------------------------------------------------------|--------|
| Bare `/goal-runner` may not resolve because plugins are namespaced | Check in step 1. Document the namespaced name in the README    | medium |
| The skill drifts as /goal changes (fast-moving feature)          | Facts and sources in best-practices.md, with a dated "verified" line | medium |
| Too many interview questions are tedious                         | Pre-fill from recon. Skip sections recon already answers        | medium |
| The subjective-word lint flags false positives                   | Lint only the condition, not the brief. Warnings, not errors    | low    |

## Checklist

- [ ] 0. Scaffolding: rename branch to `main`; add README, .gitignore,
      docs/adr/, docs/backlog/. Write ADR 0001 (plugin + NEXTGOAL.md +
      goal-runner handoff over `/goal @file` and a shell launcher). Copy
      this plan to docs/plan.md.
- [ ] 1. Spike: build a minimal plugin, load it with `claude --plugin-dir .`,
      and confirm the invocation name of goal-runner.
- [ ] 2. Write the failing pytest cases for validate_goal.py first
      (good brief passes; each rule has a failing fixture).
- [ ] 3. Implement validate_goal.py until the tests are green.
- [ ] 4. Write references/best-practices.md, template.md and interview.md.
- [ ] 5. Draft skills/goal-definer/SKILL.md with skill-creator (with an
      Explore research step).
- [ ] 6. Draft skills/goal-runner/SKILL.md with skill-creator.
- [ ] 6b. Run the skill-creator evals: the signal words trigger both skills,
      unrelated prompts don't trigger them, and a full interview run works.
      Tune the descriptions until the evals pass.
- [ ] 7. Add plugin.json and marketplace.json, install locally, and document it in the README.
- [ ] 8. Acceptance: `uv run pytest` is green. In a scratch repo, the
      goal-definer interview produces a NEXTGOAL.md that passes the validator.
      In a fresh session, goal-runner shows the summary, asks for
      confirmation, and prints a `/goal` line that, when pasted, starts
      and evaluates the goal. The `/goal` evaluator status shows the condition.
