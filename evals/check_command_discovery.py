"""Check that a request off the skill's short list makes Claude ask sc's help first.

Usage: uv run python evals/check_command_discovery.py

Runs 3 fresh `claude -p` sessions with plugins/finance and the prompt
"What's the current quote for IE00B4L5Y983?", prints only the Bash commands
each one called, and ends with `N/3 PASS`. A run passes if an sc help call
(`sc help`, `sc capabilities`, or an sc command with `--help` or `-h`) comes
before `sc broker quote` with `--isin IE00B4L5Y983` and `--json`, and no
WebFetch or mcp__ tool was called: the built-in help answers this request,
so the manual is not needed. Needs sc installed and logged in.

The raw stream-json holds sc output, so it goes to a temp directory outside
the repo and is never printed.
"""
import re
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from check_portfolio_trigger import Run, is_help_call, parse_run, run_session  # noqa: F401  Run and parse_run are used by the tests

ISIN = "IE00B4L5Y983"
PROMPT = f"What's the current quote for {ISIN}?"
RUNS = 3
QUOTE = re.compile(r"\bsc broker quote\b")
# Read-only tools only. WebFetch stays out: a denied attempt still shows up
# as a tool_use and fails the run.
ALLOWED_TOOLS = [
    "Read",
    "Bash(python -I:*)",
    "Bash(sc --help)",
    "Bash(sc -h)",
    "Bash(sc --version)",
    "Bash(sc whoami:*)",
    "Bash(sc help:*)",
    "Bash(sc capabilities:*)",
    "Bash(sc broker --help)",
    "Bash(sc broker -h)",
    "Bash(sc broker quote:*)",
]


def is_quote(command):
    return bool(QUOTE.search(command)) and f"--isin {ISIN}" in command and "--json" in command


def is_hit(run):
    if run.mcp_tools or run.web_fetches:
        return False
    help_seen = False
    for command in run.bash_commands:
        match = QUOTE.search(command)
        if is_quote(command) and not is_help_call(command[match.start():]):
            # Help earlier in the same chain counts: `sc help broker quote && sc broker quote ...`.
            return help_seen or is_help_call(command[:match.start()])
        help_seen = help_seen or is_help_call(command)
    return False


def main():
    raw_dir = Path(tempfile.mkdtemp(prefix="command-discovery-raw-"))
    raw_paths = [raw_dir / f"run-{i}.jsonl" for i in range(1, RUNS + 1)]
    with ThreadPoolExecutor(max_workers=RUNS) as pool:
        runs = list(pool.map(lambda path: run_session(path, PROMPT, ALLOWED_TOOLS), raw_paths))

    passed = 0
    for i, run in enumerate(runs, 1):
        hit = is_hit(run)
        passed += hit
        print(f"Run {i}: {'PASS' if hit else 'FAIL'}")
        for command in run.bash_commands:
            print(f"  $ {command}")
    print(f"Raw stream-json: {raw_dir}")
    print(f"{passed}/{RUNS} PASS")
    return 0 if passed == RUNS else 1


if __name__ == "__main__":
    sys.exit(main())
