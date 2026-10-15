import subprocess
import sys
from pathlib import Path

LAUNCHER = Path(__file__).parent.parent / "scripts" / "validate_goal.sh"


def run_launcher(bin_dir):
    # PATH holds only bin_dir, so the launcher sees exactly the interpreters the test provides.
    return subprocess.run(
        ["/bin/sh", str(LAUNCHER)],
        capture_output=True,
        text=True,
        env={"PATH": str(bin_dir)},
    )


def test_falls_back_to_python3_when_python_is_missing(tmp_path):
    (tmp_path / "python3").symlink_to(sys.executable)

    result = run_launcher(tmp_path)

    assert result.returncode == 2
    assert "usage: validate_goal.py" in result.stderr + result.stdout


def test_prefers_python_when_present(tmp_path):
    marker = tmp_path / "used-python"
    fake_python = tmp_path / "python"
    fake_python.write_text(f'#!/bin/sh\n: > "{marker}"\nexec "{sys.executable}" "$@"\n')
    fake_python.chmod(0o755)
    (tmp_path / "python3").symlink_to(sys.executable)

    result = run_launcher(tmp_path)

    assert result.returncode == 2
    assert marker.exists()
