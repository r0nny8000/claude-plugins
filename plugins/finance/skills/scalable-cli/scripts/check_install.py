"""Report whether the Scalable CLI `sc` is installed, current and logged in.

Usage: python check_install.py

Prints one JSON object. `findings` lists what the user still has to fix:
not_installed, update_available, not_logged_in, refresh_retryable. An empty
list means sc is ready. The script only runs `sc --version` and `sc whoami`
and never prints their output, so no account data reaches the transcript.
"""
import json
import platform
import re
import shutil
import subprocess
import urllib.request

LATEST_RELEASE_URL = "https://api.github.com/repos/ScalableCapital/scalable-cli/releases/latest"


def parse_version(text):
    # Assumed: `sc --version` prints the version as X.Y.Z somewhere in its
    # output (upstream documents the command, not its format).
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", text or "")
    return tuple(int(part) for part in match.groups()) if match else None


def latest_version():
    """Return the latest release as (X, Y, Z), or None when GitHub can't be reached."""
    try:
        with urllib.request.urlopen(LATEST_RELEASE_URL, timeout=10) as response:
            return parse_version(json.load(response).get("tag_name"))
    except (OSError, ValueError):
        # Offline or rate-limited: skip the update check rather than fail it.
        return None


def check():
    libc, libc_version = platform.libc_ver()
    report = {
        "system": platform.system(),
        "machine": platform.machine(),
        "libc": f"{libc} {libc_version}".strip() or None,
        "installed": False,
        "path": None,
        "version": None,
        "latest_version": None,
        "logged_in": None,
        "findings": [],
    }
    latest = latest_version()
    report["latest_version"] = ".".join(map(str, latest)) if latest else None

    path = shutil.which("sc")
    if path is None:
        report["findings"].append("not_installed")
        return report
    report["installed"] = True
    report["path"] = path

    result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=30)
    installed = parse_version(result.stdout + result.stderr)
    report["version"] = ".".join(map(str, installed)) if installed else None
    if installed and latest and installed < latest:
        report["findings"].append("update_available")

    # Assumed: `sc whoami` exits 0 with a valid session and non-zero without
    # one. Upstream documents only exit code 30 (refresh_retryable: retry the
    # same command, no new login needed), so every other non-zero code counts
    # as logged out.
    whoami = subprocess.run([path, "whoami"], capture_output=True, text=True, timeout=30)
    report["logged_in"] = whoami.returncode == 0
    if whoami.returncode == 30:
        report["findings"].append("refresh_retryable")
    elif whoami.returncode != 0:
        report["findings"].append("not_logged_in")
    return report


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
