"""Check a goal file (docs/backlog/goal-<slug>.md) before it is handed to /goal.

Usage: python validate_goal.py <path> [--print-condition]

Stdlib only, so the plugin runs it with plain `python` and no install step.
Exit code 0 means no errors (warnings allowed), 1 means at least one error,
2 means wrong usage.
"""

import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "Goal",
    "Context",
    "Acceptance checklist",
    "Verification",
    "Guardrails",
    "Out of scope",
    "Open questions",
    "Condition",
]

# /goal rejects conditions longer than this (code.claude.com/docs/en/goal).
MAX_CONDITION_CHARS = 4000

STOP_CLAUSE = re.compile(r"stop after \d+\s*(turns?|minutes?|hours?)", re.IGNORECASE)
BACKTICKED = re.compile(r"`[^`]+`")
CHECKLIST_ITEM = re.compile(r"^\s*- \[ \] ", re.MULTILINE)
TEST_INTEGRITY = re.compile(r"\btests?\b.*\b(delet|skip|weaken|disabl)", re.IGNORECASE)
NO_OPEN_QUESTIONS = {"", "none", "-", "n/a"}

# The evaluator can't judge taste. "clean" is deliberately absent because
# "`git status` is clean" is a legitimate, checkable condition.
SUBJECTIVE_WORDS = re.compile(
    r"\b(better|cleaner|nicer|nice|improved?|improves|elegant|readable|beautiful|optimal)\b",
    re.IGNORECASE,
)


def split_sections(text):
    sections = {}
    current = None
    for line in text.splitlines():
        heading = re.match(r"^## (.+?)\s*$", line)
        if heading:
            current = heading.group(1)
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def extract_condition(condition_section):
    match = re.search(r"```text\n(.*?)\n```", condition_section, re.DOTALL)
    if not match:
        return None
    return match.group(1).strip()


def validate(text):
    errors = []
    warnings = []
    sections = split_sections(text)

    for name in REQUIRED_SECTIONS:
        if name not in sections:
            errors.append(f"missing section: {name}")

    if "Acceptance checklist" in sections and not CHECKLIST_ITEM.search(
        sections["Acceptance checklist"]
    ):
        errors.append("acceptance checklist has no '- [ ]' items")

    if "Guardrails" in sections and not TEST_INTEGRITY.search(sections["Guardrails"]):
        errors.append(
            "guardrails lack a test-integrity rule "
            "(e.g. 'No test is deleted, skipped, or weakened')"
        )

    if "Open questions" in sections:
        if sections["Open questions"].strip().lower() not in NO_OPEN_QUESTIONS:
            errors.append("open questions remain; resolve them before handoff")

    if "Condition" in sections:
        condition = extract_condition(sections["Condition"])
        if not condition:
            errors.append("no condition block: put the condition in a ```text fence")
        else:
            if len(condition) > MAX_CONDITION_CHARS:
                errors.append(
                    f"condition is {len(condition)} chars; /goal allows {MAX_CONDITION_CHARS}"
                )
            if not STOP_CLAUSE.search(condition):
                errors.append("condition has no stop clause (e.g. 'or stop after 20 turns')")
            if not BACKTICKED.search(condition):
                errors.append("condition names no check command in backticks")
            # Commands and branch names in backticks are literal, not claims.
            prose = BACKTICKED.sub("", condition)
            for word in sorted({m.group(0).lower() for m in SUBJECTIVE_WORDS.finditer(prose)}):
                warnings.append(f"subjective word in condition: '{word}'")

    return errors, warnings


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print("usage: validate_goal.py <goal-file> [--print-condition]")
        return 2
    path = Path(args[0])

    if not path.exists():
        print(f"ERROR: {path} not found")
        return 1
    text = path.read_text()

    if "--print-condition" in argv:
        condition = extract_condition(split_sections(text).get("Condition", ""))
        if not condition:
            print("ERROR: no condition block found")
            return 1
        print(condition)
        return 0

    errors, warnings = validate(text)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    print("FAILED" if errors else "OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
