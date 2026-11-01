"""Check that "What's my portfolio worth?" makes Claude call `sc broker overview --json`.

Usage: uv run python evals/check_portfolio_trigger.py

Runs 3 fresh `claude -p` sessions with plugins/finance, prints only the Bash
commands each one called, and ends with `N/3 PASS`. A run passes if a Bash
call contains `sc broker overview` with `--json` and no mcp__ tool was called.
Needs sc installed and logged in.

The raw stream-json holds sc output, which is account data, so it goes to a
temp directory outside the repo and is never printed.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent / "plugins" / "finance"
PROMPT = "What's my portfolio worth?"
RUNS = 3
OVERVIEW = re.compile(r"\bsc broker overview\b")
# Read-only tools only: the skill's references, its check script, and sc
# commands that read. Anything else is denied but still shows up as an attempt.
ALLOWED_TOOLS = [
    "Read",
    "Bash(python -I:*)",
    "Bash(sc --help)",
    "Bash(sc --version)",
    "Bash(sc whoami:*)",
    "Bash(sc capabilities:*)",
    "Bash(sc broker --help)",
    "Bash(sc broker overview:*)",
]


@dataclass
class Run:
    bash_commands: list
    mcp_tools: list


def parse_run(lines):
    """Collect the Bash commands and mcp__ tool names from stream-json lines."""
    run = Run([], [])
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = event.get("message")
        if event.get("type") != "assistant" or not isinstance(message, dict):
            continue
        for item in message.get("content") or []:
            if not isinstance(item, dict) or item.get("type") != "tool_use":
                continue
            if item.get("name") == "Bash":
                run.bash_commands.append(item["input"].get("command", ""))
            elif item.get("name", "").startswith("mcp__"):
                run.mcp_tools.append(item["name"])
    return run


def is_hit(run):
    # An MCP call means a connector could have answered instead of sc.
    if run.mcp_tools:
        return False
    return any(OVERVIEW.search(c) and "--json" in c for c in run.bash_commands)


def run_session(raw_path):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    # The claude.ai Scalable connector must not answer instead of sc.
    env["ENABLE_CLAUDEAI_MCP_SERVERS"] = "false"
    command = [
        "claude", "-p", PROMPT, "--plugin-dir", str(PLUGIN_DIR), "--strict-mcp-config",
        "--output-format", "stream-json", "--verbose", "--max-turns", "10",
        "--permission-mode", "default", "--allowedTools", *ALLOWED_TOOLS,
    ]
    with open(raw_path, "w") as raw:
        subprocess.run(command, stdout=raw, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, text=True,
                       env=env, cwd=tempfile.mkdtemp(prefix="portfolio-trigger-"))
    with open(raw_path) as raw:
        return parse_run(raw)


def main():
    raw_dir = Path(tempfile.mkdtemp(prefix="portfolio-trigger-raw-"))
    raw_paths = [raw_dir / f"run-{i}.jsonl" for i in range(1, RUNS + 1)]
    with ThreadPoolExecutor(max_workers=RUNS) as pool:
        runs = list(pool.map(run_session, raw_paths))

    passed = 0
    for i, run in enumerate(runs, 1):
        hit = is_hit(run)
        passed += hit
        print(f"Run {i}: {'PASS' if hit else 'FAIL'}")
        for command in run.bash_commands:
            print(f"  $ {command}")
        for tool in run.mcp_tools:
            print(f"  mcp call: {tool}")
    print(f"Raw stream-json: {raw_dir}")
    print(f"{passed}/{RUNS} PASS")
    return 0 if passed == RUNS else 1


if __name__ == "__main__":
    sys.exit(main())
