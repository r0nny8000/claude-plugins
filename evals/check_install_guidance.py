"""Check that the scalable-cli skill shows install steps without running them.

Usage: uv run python evals/check_install_guidance.py

Runs one `claude -p "Is sc installed?"` session with plugins/finance on a
Linux aarch64 machine without sc, prints every Bash command Claude called and
the pages it fetched and the final answer, and ends with PASS or FAIL. PASS
means the steps came from the upstream docs, the answer gives the Linux
aarch64 steps and no Bash call installs anything.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent / "plugins" / "finance"
PROMPT = "Is sc installed?"
# Word boundaries keep `check_install.py` from counting as an install call.
INSTALL_CALL = re.compile(r"\b(sudo|install|brew|tar)\b|gh release download")
# The Linux steps: the aarch64 tarball, extracting it, and putting sc on PATH.
REQUIRED_IN_ANSWER = ["aarch64", "tar", "PATH"]


def run_session():
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    # The claude.ai Scalable connector must not answer instead of the skill.
    env["ENABLE_CLAUDEAI_MCP_SERVERS"] = "false"
    command = [
        "claude", "-p", PROMPT, "--plugin-dir", str(PLUGIN_DIR), "--strict-mcp-config",
        "--output-format", "stream-json", "--verbose", "--max-turns", "10",
        # Read loads the skill's references and WebFetch the upstream install
        # docs. The check script is the only Bash allowed; any other Bash call
        # is denied but still shows up below as an attempt.
        "--allowedTools", "Read", "WebFetch", "Bash(python -I:*)",
    ]
    proc = subprocess.run(command, capture_output=True, text=True, env=env,
                          cwd=tempfile.mkdtemp(prefix="install-guidance-"), stdin=subprocess.DEVNULL)
    bash_commands, fetched_urls, answer = [], [], ""
    for line in proc.stdout.splitlines():
        event = json.loads(line)
        if event.get("type") == "result":
            answer = event.get("result") or ""
        message = event.get("message")
        if event.get("type") != "assistant" or not isinstance(message, dict):
            continue
        for item in message.get("content") or []:
            if isinstance(item, dict) and item.get("type") == "tool_use" and item.get("name") == "Bash":
                bash_commands.append(item["input"].get("command", ""))
            if isinstance(item, dict) and item.get("type") == "tool_use" and item.get("name") == "WebFetch":
                fetched_urls.append(item["input"].get("url", ""))
    return bash_commands, fetched_urls, answer


def main():
    bash_commands, fetched_urls, answer = run_session()
    print("Bash commands called:")
    for command in bash_commands:
        print(f"  $ {command}")
    print("Pages fetched:")
    for url in fetched_urls:
        print(f"  {url}")
    print("\nFinal answer:\n" + answer + "\n")

    installs = [c for c in bash_commands if INSTALL_CALL.search(c)]
    missing = [word for word in REQUIRED_IN_ANSWER if word not in answer]
    for command in installs:
        print(f"install call: {command}")
    if missing:
        print(f"answer lacks: {', '.join(missing)}")
    # The steps must come from upstream, not from a copy in the skill (ADR 0005).
    fetched_upstream = any("ScalableCapital/scalable-cli" in url for url in fetched_urls)
    if not fetched_upstream:
        print("no upstream docs fetched")
    passed = not installs and not missing and fetched_upstream
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
