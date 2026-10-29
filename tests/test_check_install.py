import importlib.util
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).parent.parent
    / "plugins" / "finance" / "skills" / "scalable-cli" / "scripts" / "check_install.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("check_install", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def check_install(monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "latest_version", lambda: (1, 2, 0))
    return module


def fake_sc(tmp_path, monkeypatch, version="sc 1.2.0", whoami_exit=0):
    """Put a stand-in `sc` on PATH that answers --version and whoami."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    sc = bin_dir / "sc"
    sc.write_text(
        "#!/bin/sh\n"
        f'if [ "$1" = "--version" ]; then echo "{version}"; exit 0; fi\n'
        f'if [ "$1" = "whoami" ]; then exit {whoami_exit}; fi\n'
        "exit 2\n"
    )
    sc.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir))


def test_not_installed(check_install, tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))
    report = check_install.check()
    assert report["findings"] == ["not_installed"]
    assert report["installed"] is False
    assert report["latest_version"] == "1.2.0"


def test_ready_when_current_and_logged_in(check_install, tmp_path, monkeypatch):
    fake_sc(tmp_path, monkeypatch)
    report = check_install.check()
    assert report["findings"] == []
    assert report["version"] == "1.2.0"
    assert report["logged_in"] is True


def test_update_available(check_install, tmp_path, monkeypatch):
    fake_sc(tmp_path, monkeypatch, version="sc 1.1.0")
    report = check_install.check()
    assert report["findings"] == ["update_available"]
    assert report["version"] == "1.1.0"


def test_no_update_finding_when_latest_unknown(check_install, tmp_path, monkeypatch):
    monkeypatch.setattr(check_install, "latest_version", lambda: None)
    fake_sc(tmp_path, monkeypatch, version="sc 1.1.0")
    assert check_install.check()["findings"] == []


def test_not_logged_in(check_install, tmp_path, monkeypatch):
    fake_sc(tmp_path, monkeypatch, whoami_exit=1)
    report = check_install.check()
    assert report["findings"] == ["not_logged_in"]
    assert report["logged_in"] is False


def test_refresh_retryable_is_not_a_logout(check_install, tmp_path, monkeypatch):
    fake_sc(tmp_path, monkeypatch, whoami_exit=30)
    assert check_install.check()["findings"] == ["refresh_retryable"]


def test_outdated_and_logged_out_together(check_install, tmp_path, monkeypatch):
    fake_sc(tmp_path, monkeypatch, version="sc 0.9.3", whoami_exit=1)
    assert check_install.check()["findings"] == ["update_available", "not_logged_in"]
