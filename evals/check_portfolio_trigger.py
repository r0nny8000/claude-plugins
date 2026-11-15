"""Check that "What's my portfolio worth?" makes Claude call `sc broker overview --json`.

Usage: uv run python evals/check_portfolio_trigger.py

Runs 3 fresh `claude -p` sessions with plugins/finance, prints only the Bash
commands each one called, and ends with `N/3 PASS`. A run passes if a Bash
call contains `sc broker overview` with `--json`, no sc help or capabilities
call came before it, and no WebFetch or mcp__ tool was called: overview is on
the skill's short list, so Claude runs it directly. Needs sc installed and
logged in.

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
from dataclasses import dataclass, field
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent / "plugins" / "finance"
PROMPT = "What's my portfolio worth?"
RUNS = 3
OVERVIEW = re.compile(r"\bsc broker overview\b")
HELP_CALL = re.compile(r"\bsc (help|capabilities)\b|\bsc\b.*(--help\b| -h\b)")
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
    "Bash(sc broker cash-breakdown:*)",
    "Bash(sc broker holdings:*)",
]


@dataclass
class Run:
    bash_commands: list
    mcp_tools: list
    web_fetches: list = field(default_factory=list)


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
            elif item.get("name") == "WebFetch":
                run.web_fetches.append(item["input"].get("url", ""))
            elif item.get("name", "").startswith("mcp__"):
                run.mcp_tools.append(item["name"])
    return run


def is_help_call(command):
    return bool(HELP_CALL.search(command))


def is_hit(run):
    # An MCP call means a connector could have answered instead of sc; a
    # WebFetch means Claude read the manual for a command it already knows.
    if run.mcp_tools or run.web_fetches:
        return False
    for command in run.bash_commands:
        match = OVERVIEW.search(command)
        if match and "--json" in command:
            # A chained `sc capabilities --json && sc broker overview --json` is help first too.
            return not is_help_call(command[:match.start()])
        if is_help_call(command):
            return False
    return False


def run_session(raw_path, prompt=PROMPT, allowed_tools=ALLOWED_TOOLS):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    # The claude.ai Scalable connector must not answer instead of sc.
    env["ENABLE_CLAUDEAI_MCP_SERVERS"] = "false"
    command = [
        "claude", "-p", prompt, "--plugin-dir", str(PLUGIN_DIR), "--strict-mcp-config",
        "--output-format", "stream-json", "--verbose", "--max-turns", "10",
        "--permission-mode", "default", "--allowedTools", *allowed_tools,
    ]
    with open(raw_path, "w") as raw, tempfile.TemporaryDirectory(prefix="portfolio-trigger-") as work_dir:
        subprocess.run(command, stdout=raw, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, text=True,
                       env=env, cwd=work_dir)
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
        for url in run.web_fetches:
            print(f"  web fetch: {url}")
        for tool in run.mcp_tools:
            print(f"  mcp call: {tool}")
    print(f"Raw stream-json: {raw_dir}")
    print(f"{passed}/{RUNS} PASS")
    return 0 if passed == RUNS else 1


if __name__ == "__main__":
    sys.exit(main())
