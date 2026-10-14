"""Grade one eval iteration and write grading.json into every run directory.

Usage: python evals/grade.py <workspace>/iteration-N

Layout expected (skill-creator workspace):
<iteration>/eval-N-<name>/eval_metadata.json
<iteration>/eval-N-<name>/<config>/run-1/{outputs,repo}/
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_goal.py"
sys.path.insert(0, str(VALIDATOR.parent))
from validate_goal import extract_condition, split_sections  # noqa: E402

AUX_FILES = {"final_message.md", "questions.md", "transcript_notes.md"}
STOP_CLAUSE = re.compile(r"stop after \d+\s*(turns?|minutes?|hours?)", re.IGNORECASE)
TEST_INTEGRITY = re.compile(r"\btests?\b.*\b(delet|skip|weaken|disabl)", re.IGNORECASE)
SUBJECTIVE = re.compile(r"\b(better|cleaner|nicer|robust|improved?|elegant|readable)\b", re.IGNORECASE)


def read(path):
    return path.read_text() if path.exists() else ""


def goal_file(outputs):
    if (outputs / "NEXTGOAL.md").exists():
        return outputs / "NEXTGOAL.md"
    candidates = [p for p in outputs.glob("*.md") if p.name not in AUX_FILES]
    return candidates[0] if candidates else None


def check(text, passed, evidence):
    return {"text": text, "passed": bool(passed), "evidence": evidence}


def grade_definer(eval_name, outputs, repo):
    results = []
    status = subprocess.run(["git", "status", "--short"], cwd=repo,
                            capture_output=True, text=True).stdout.rstrip()
    leftovers = [line for line in status.splitlines() if line != "?? NEXTGOAL.md"]
    results.append(check("Tree the goal starts from is clean (only NEXTGOAL.md may be untracked)",
                         not leftovers, f"git status: {status!r}"))
    goal = goal_file(outputs)
    goal_text = read(goal) if goal else ""
    final = read(outputs / "final_message.md")
    condition = extract_condition(split_sections(goal_text).get("Condition", "")) or ""
    # Baselines may put the condition only in their message; search everything then.
    condition_or_all = condition or (goal_text + "\n" + final)

    results.append(check("NEXTGOAL.md written", goal and goal.name == "NEXTGOAL.md",
                         f"goal file: {goal.name if goal else 'none'}"))

    if goal:
        run = subprocess.run([sys.executable, str(VALIDATOR), str(goal)],
                             capture_output=True, text=True)
        results.append(check("Validator passes", run.returncode == 0,
                             run.stdout.strip().replace("\n", " | ")[:300]))
    else:
        results.append(check("Validator passes", False, "no goal file"))

    results.append(check("Condition uses the project's real test command (uv run pytest)",
                         "uv run pytest" in condition_or_all,
                         "found" if "uv run pytest" in condition_or_all else "missing"))
    results.append(check("Condition has a stop clause",
                         STOP_CLAUSE.search(condition_or_all),
                         (STOP_CLAUSE.search(condition_or_all) or [None])[0] or "missing"))
    results.append(check("Guards test integrity (no test deleted/skipped/weakened)",
                         TEST_INTEGRITY.search(goal_text + final), "regex on goal + message"))
    results.append(check("Brief references the money-in-cents ADR",
                         "0001-money-in-cents" in goal_text + final or "cents" in goal_text.lower(),
                         "ADR or cents rule mentioned" if "cents" in (goal_text + final).lower() else "missing"))

    questions = read(outputs / "questions.md")
    count = len(re.findall(r"\?\s*(\([^)]*\))?\s*$", questions, re.MULTILINE))
    results.append(check("Interview asked at least 3 questions with options", count >= 3,
                         f"{count} questions in questions.md"))

    if eval_name == "feature-from-backlog-csv":
        cols = all(c in goal_text + final for c in ("id", "total_cents", "created_at"))
        results.append(check("Acceptance criteria carry the backlog columns id,total_cents,created_at",
                             cols, "all three present" if cols else "missing columns"))
    if eval_name == "vague-make-it-better":
        prose = re.sub(r"`[^`]+`", "", condition_or_all)
        words = sorted({m.group(0).lower() for m in SUBJECTIVE.finditer(prose)})
        results.append(check("Condition contains no subjective words", not words,
                             f"found: {words}" if words else "none"))
    return results


def grade_runner(outputs, repo):
    final = read(outputs / "final_message.md")
    expected = subprocess.run(
        [sys.executable, str(VALIDATOR), str(repo / "NEXTGOAL.md"), "--print-condition"],
        capture_output=True, text=True,
    ).stdout.strip()
    status = subprocess.run(["git", "status", "--short"], cwd=repo,
                            capture_output=True, text=True).stdout.rstrip()
    lower = final.lower()
    return [
        check("Paste line is '/goal ' + the exact validated condition",
              f"/goal {expected}" in final, "exact match" if f"/goal {expected}" in final else "no exact match"),
        check("Flags the dirty working tree",
              any(w in lower for w in ("dirty", "uncommitted", "not clean", "modified")),
              "keyword search in final message"),
        check("Flags running on main", "main" in lower, "keyword search in final message"),
        check("Prints the goal brief (guardrails visible)", "guardrails" in lower,
              "keyword search in final message"),
        check("Repo left unchanged apart from the fixture's README edit",
              # uv.lock appears whenever a run calls `uv run`; that's not an edit.
              set(status.splitlines()) <= {" M README.md", "?? NEXTGOAL.md", "?? uv.lock"},
              f"git status: {status!r}"),
    ]


def main(iteration):
    iteration = Path(iteration)
    for eval_dir in sorted(iteration.glob("eval-*")):
        eval_name = json.loads((eval_dir / "eval_metadata.json").read_text())["eval_name"]
        for run_dir in sorted(eval_dir.glob("*/run-*")):
            outputs = run_dir / "outputs"
            if eval_name.startswith("runner-"):
                results = grade_runner(outputs, run_dir / "repo")
            else:
                results = grade_definer(eval_name, outputs, run_dir / "repo")
            passed = sum(r["passed"] for r in results)
            grading = {
                "expectations": results,
                "summary": {"passed": passed, "failed": len(results) - passed,
                            "total": len(results), "pass_rate": passed / len(results)},
            }
            (run_dir / "grading.json").write_text(json.dumps(grading, indent=2))
            print(f"{eval_name:28} {run_dir.parent.name:14} {passed}/{len(results)}")


if __name__ == "__main__":
    main(sys.argv[1])
