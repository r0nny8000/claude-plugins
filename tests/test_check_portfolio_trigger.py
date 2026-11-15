import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "evals" / "check_portfolio_trigger.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_portfolio_trigger", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assistant(*tool_uses):
    content = [{"type": "tool_use", "name": name, "input": tool_input} for name, tool_input in tool_uses]
    return json.dumps({"type": "assistant", "message": {"content": content}})


def test_collects_bash_commands_and_mcp_tools_in_order():
    lines = [
        json.dumps({"type": "system", "subtype": "init"}),
        assistant(("Skill", {"skill": "finance:scalable-cli"})),
        assistant(("Bash", {"command": "python -I /x/check_install.py"})),
        json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": "secret"}]}}),
        assistant(("Bash", {"command": "sc broker overview --json"}),
                  ("mcp__claude_ai_Scalable__get_portfolio_overview", {})),
        json.dumps({"type": "result", "result": "Your portfolio is worth ..."}),
    ]
    run = load_module().parse_run(lines)
    assert run.bash_commands == ["python -I /x/check_install.py", "sc broker overview --json"]
    assert run.mcp_tools == ["mcp__claude_ai_Scalable__get_portfolio_overview"]


def test_skips_blank_and_non_json_lines():
    lines = ["", "not json", assistant(("Bash", {"command": "sc broker overview --json"}))]
    assert load_module().parse_run(lines).bash_commands == ["sc broker overview --json"]


def test_hit_needs_overview_with_json_flag():
    module = load_module()
    assert module.is_hit(module.Run(["python -I check.py", "sc broker overview --json"], []))
    assert module.is_hit(module.Run(["sc broker overview --portfolio p1 --json"], []))
    assert not module.is_hit(module.Run(["sc broker overview"], []))
    assert not module.is_hit(module.Run(["sc broker holdings --json"], []))


def test_mcp_call_fails_a_run_even_with_sc_overview():
    module = load_module()
    run = module.Run(["sc broker overview --json"], ["mcp__claude_ai_Scalable__ping"])
    assert not module.is_hit(run)


def test_collects_web_fetch_calls():
    lines = [assistant(("WebFetch", {"url": "https://example.com"}), ("Bash", {"command": "sc broker overview --json"}))]
    assert load_module().parse_run(lines).web_fetches == ["https://example.com"]


def test_web_fetch_fails_a_run_even_with_sc_overview():
    module = load_module()
    assert not module.is_hit(module.Run(["sc broker overview --json"], [], ["https://example.com"]))


def test_help_call_detection():
    module = load_module()
    for command in ["sc help broker", "sc capabilities --json", "sc --help", "sc broker -h",
                    "sc broker overview --help", "sc broker --help | head"]:
        assert module.is_help_call(command), command
    for command in ["sc broker overview --json", "sc --version", "python -I /x/scalable-cli/check_install.py",
                    "sc broker holdings --json"]:
        assert not module.is_help_call(command), command


def test_help_or_capabilities_before_overview_fails_a_run():
    module = load_module()
    assert not module.is_hit(module.Run(["sc capabilities --json", "sc broker overview --json"], []))
    assert not module.is_hit(module.Run(["sc broker --help", "sc broker overview --json"], []))
    assert not module.is_hit(module.Run(["sc capabilities --json && sc broker overview --json"], []))


def test_check_script_and_help_after_overview_still_pass():
    module = load_module()
    assert module.is_hit(module.Run(["python -I /x/check_install.py", "sc broker overview --json",
                                     "sc broker holdings --help"], []))


def test_listed_commands_are_allowed():
    tools = load_module().ALLOWED_TOOLS
    assert "Bash(sc broker cash-breakdown:*)" in tools
    assert "Bash(sc broker holdings:*)" in tools
