"""Check that the scalable-cli skill writes a one-time install script without running it.

Usage: uv run python evals/check_install_script.py

Runs one `claude -p` session with plugins/finance on a Linux aarch64 machine
without sc, asking for the install script. Prints every Bash command Claude
called, the pages it fetched and the script, and ends with PASS or FAIL.
The script is only syntax-checked with `bash -n`, never executed, and is
removed afterwards.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent / "plugins" / "finance"
SCRIPT = Path("/tmp/sc-install.sh")
PROMPT = "Is sc installed? If it's missing, write me the one-time install script."
# The lookbehind keeps `check_install.py` and `sc-install.sh` from counting
# as install calls; a plain \b treats `_` and `-` differently.
INSTALL_CALL = re.compile(r"(?<![\w-])(sudo|install|brew|tar)\b|gh release download")
# Running or chmod-ing the script counts too; reading it (ls, cat) doesn't.
RUN_SCRIPT = re.compile(r"\b(bash|sh|zsh|source|chmod)\b[^|;&]*sc-install\.sh|(^|[;&|]\s*)\S*/sc-install\.sh")


def run_session():
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    # The claude.ai Scalable connector must not answer instead of the skill.
    env["ENABLE_CLAUDEAI_MCP_SERVERS"] = "false"
    command = [
        "claude", "-p", PROMPT, "--plugin-dir", str(PLUGIN_DIR), "--strict-mcp-config",
        "--output-format", "stream-json", "--verbose", "--max-turns", "15",
        "--add-dir", str(SCRIPT.parent),
        # Bash is limited to the check script; any other call is denied but
        # still shows up below, so running the install script would fail.
        "--allowedTools", "Read", "WebFetch", "Write", "Bash(python -I:*)",
    ]
    proc = subprocess.run(command, capture_output=True, text=True, env=env,
                          cwd=tempfile.mkdtemp(prefix="install-script-"), stdin=subprocess.DEVNULL)
    bash_commands, fetched_urls, answer = [], [], ""
    for line in proc.stdout.splitlines():
        event = json.loads(line)
        if event.get("type") == "result":
            answer = event.get("result") or ""
        message = event.get("message")
        if event.get("type") != "assistant" or not isinstance(message, dict):
            continue
        for item in message.get("content") or []:
            if not isinstance(item, dict) or item.get("type") != "tool_use":
                continue
            if item.get("name") == "Bash":
                bash_commands.append(item["input"].get("command", ""))
            if item.get("name") == "WebFetch":
                fetched_urls.append(item["input"].get("url", ""))
    return bash_commands, fetched_urls, answer


def script_problems(text):
    problems = []
    syntax = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
    if syntax.returncode != 0:
        problems.append(f"bash -n failed: {syntax.stderr.strip()}")
    checks = [
        ("set -euo pipefail" in text, "no `set -euo pipefail`"),
        ("linux" in text and "aarch64" in text, "no linux aarch64 asset"),
        ("SHA256SUMS" in text and "sha256sum" in text, "no SHA256 checksum check"),
        # $0 can be relative, so it must be resolved before any cd.
        ('realpath -- "$0"' in text and re.search(r'^rm (-f )?-- "\$\{?\w+\}?"$', text, re.M),
         'no self-delete via realpath -- "$0" and a final rm --'),
        (not re.search(r"^[^#\n]*\bsudo\b", text, re.M), "uses sudo"),
    ]
    problems += [message for ok, message in checks if not ok]
    # sc login may appear in comments or echoed hints, never as a command:
    # a line that starts with sc (or a path ending in /sc) followed by login.
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"\S*\bsc\"? login\b", stripped):
            problems.append(f"runs sc login: {stripped}")
    return problems


def main():
    if SCRIPT.exists():
        print(f"{SCRIPT} already exists; move it away first so this check doesn't overwrite it.")
        return 2
    try:
        bash_commands, fetched_urls, answer = run_session()
        print("Bash commands called:")
        for command in bash_commands:
            print(f"  $ {command}")
        print("Pages fetched:")
        for url in fetched_urls:
            print(f"  {url}")
        print("\nFinal answer:\n" + answer + "\n")

        problems = [f"install call: {c}" for c in bash_commands if INSTALL_CALL.search(c) or RUN_SCRIPT.search(c)]
        if not any("ScalableCapital/scalable-cli" in url for url in fetched_urls):
            problems.append("no upstream docs fetched")
        if SCRIPT.exists():
            text = SCRIPT.read_text()
            print(f"--- {SCRIPT}\n{text}\n---")
            problems += script_problems(text)
        else:
            problems.append(f"{SCRIPT} not written")
    finally:
        SCRIPT.unlink(missing_ok=True)

    for problem in problems:
        print(problem)
    print("PASS" if not problems else "FAIL")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
