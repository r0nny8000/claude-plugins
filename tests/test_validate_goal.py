import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "validate_goal.py"

GOOD_CONDITION = (
    "All tests in tests/auth pass as shown by `uv run pytest tests/auth` exiting 0; "
    "`ruff check .` exits 0; guardrails: no test is deleted, skipped or weakened, "
    "no edits outside src/auth and tests/auth; out of scope: UI changes. "
    "Show the output of each check in the transcript. "
    "Or stop after 20 turns and report what remains."
)

GOOD_BRIEF = f"""# NEXTGOAL: Fix token refresh

## Goal

Expired sessions refresh their token instead of logging the user out.

## Context

- Repo state: branch fix/token-refresh, clean tree
- Relevant files: src/auth/session.py

## Acceptance checklist

- [ ] Refresh test passes — proven by `uv run pytest tests/auth` exits 0
- [ ] Lint is clean — proven by `ruff check .` exits 0

## Verification

`uv run pytest` exits 0; show the output in the transcript.

## Guardrails

- No test is deleted, skipped, or weakened to make a check pass.
- No edits outside src/auth and tests/auth.

## Out of scope

- UI changes

## Approach hints

- Look at the refresh path in session.py first.

## Open questions

None

## Condition

```text
{GOOD_CONDITION}
```
"""


def run(tmp_path, text, *args):
    path = tmp_path / "NEXTGOAL.md"
    path.write_text(text)
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path), *args],
        capture_output=True,
        text=True,
    )


def test_good_brief_passes(tmp_path):
    result = run(tmp_path, GOOD_BRIEF)
    assert result.returncode == 0, result.stdout
    assert "ERROR" not in result.stdout


def test_missing_file_fails(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path / "NEXTGOAL.md")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "not found" in result.stdout


@pytest.mark.parametrize(
    "section",
    [
        "Goal",
        "Context",
        "Acceptance checklist",
        "Verification",
        "Guardrails",
        "Out of scope",
        "Open questions",
        "Condition",
    ],
)
def test_missing_required_section_fails(tmp_path, section):
    text = GOOD_BRIEF.replace(f"## {section}\n", "## Renamed\n", 1)
    result = run(tmp_path, text)
    assert result.returncode == 1
    assert f"missing section: {section}" in result.stdout


def test_approach_hints_is_optional(tmp_path):
    text = GOOD_BRIEF.replace(
        "## Approach hints\n\n- Look at the refresh path in session.py first.\n\n", ""
    )
    result = run(tmp_path, text)
    assert result.returncode == 0, result.stdout


def test_condition_without_text_block_fails(tmp_path):
    text = GOOD_BRIEF.replace("```text\n", "").replace("\n```\n", "\n")
    result = run(tmp_path, text)
    assert result.returncode == 1
    assert "condition block" in result.stdout


def test_condition_over_4000_chars_fails(tmp_path):
    long_condition = GOOD_CONDITION + " Padding." * 450
    text = GOOD_BRIEF.replace(GOOD_CONDITION, long_condition)
    result = run(tmp_path, text)
    assert result.returncode == 1
    assert "4000" in result.stdout


def test_condition_without_stop_clause_fails(tmp_path):
    text = GOOD_BRIEF.replace(" Or stop after 20 turns and report what remains.", "")
    result = run(tmp_path, text)
    assert result.returncode == 1
    assert "stop clause" in result.stdout


def test_time_based_stop_clause_passes(tmp_path):
    text = GOOD_BRIEF.replace("stop after 20 turns", "stop after 45 minutes")
    result = run(tmp_path, text)
    assert result.returncode == 0, result.stdout


def test_condition_without_backticked_command_fails(tmp_path):
    condition = GOOD_CONDITION.replace("`", "")
    text = GOOD_BRIEF.replace(GOOD_CONDITION, condition)
    result = run(tmp_path, text)
    assert result.returncode == 1
    assert "check command" in result.stdout


def test_guardrails_without_test_integrity_rule_fails(tmp_path):
    text = GOOD_BRIEF.replace(
        "- No test is deleted, skipped, or weakened to make a check pass.\n", ""
    )
    result = run(tmp_path, text)
    assert result.returncode == 1
    assert "test-integrity" in result.stdout


def test_checklist_without_items_fails(tmp_path):
    text = GOOD_BRIEF.replace("- [ ] ", "- ")
    result = run(tmp_path, text)
    assert result.returncode == 1
    assert "checklist" in result.stdout


def test_open_questions_left_fails(tmp_path):
    text = GOOD_BRIEF.replace(
        "## Open questions\n\nNone\n", "## Open questions\n\n- Which branch?\n"
    )
    result = run(tmp_path, text)
    assert result.returncode == 1
    assert "open questions" in result.stdout


def test_subjective_word_in_condition_warns_but_passes(tmp_path):
    condition = GOOD_CONDITION.replace("All tests", "The code is better and all tests")
    text = GOOD_BRIEF.replace(GOOD_CONDITION, condition)
    result = run(tmp_path, text)
    assert result.returncode == 0, result.stdout
    assert "WARNING" in result.stdout
    assert "better" in result.stdout


def test_git_status_is_clean_does_not_warn(tmp_path):
    condition = GOOD_CONDITION.replace("; guardrails", "; `git status` is clean; guardrails")
    text = GOOD_BRIEF.replace(GOOD_CONDITION, condition)
    result = run(tmp_path, text)
    assert result.returncode == 0, result.stdout
    assert "WARNING" not in result.stdout


def test_subjective_word_inside_backticks_does_not_warn(tmp_path):
    condition = GOOD_CONDITION.replace("; guardrails", "; `git switch better-errors` succeeds; guardrails")
    text = GOOD_BRIEF.replace(GOOD_CONDITION, condition)
    result = run(tmp_path, text)
    assert result.returncode == 0, result.stdout
    assert "WARNING" not in result.stdout


def test_print_condition_outputs_only_the_condition(tmp_path):
    result = run(tmp_path, GOOD_BRIEF, "--print-condition")
    assert result.returncode == 0
    assert result.stdout.strip() == GOOD_CONDITION
