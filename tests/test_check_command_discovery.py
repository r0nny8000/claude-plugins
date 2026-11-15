import importlib.util
import json
import sys
from pathlib import Path

EVALS = Path(__file__).parent.parent / "evals"
SCRIPT = EVALS / "check_command_discovery.py"


def load_module():
    # The eval imports check_portfolio_trigger from its own directory, as it does when run as a script.
    sys.path.insert(0, str(EVALS))
    spec = importlib.util.spec_from_file_location("check_command_discovery", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assistant(*tool_uses):
    content = [{"type": "tool_use", "name": name, "input": tool_input} for name, tool_input in tool_uses]
    return json.dumps({"type": "assistant", "message": {"content": content}})


QUOTE = "sc broker quote --isin IE00B4L5Y983 --json"


def test_prompt_asks_for_the_quote():
    assert load_module().PROMPT == "What's the current quote for IE00B4L5Y983?"


def test_parses_bash_web_fetch_and_mcp_calls():
    lines = [
        "not json",
        assistant(("Bash", {"command": "sc broker quote --help"})),
        json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": "secret"}]}}),
        assistant(("WebFetch", {"url": "https://github.com/x"}), ("mcp__claude_ai_Scalable__quote", {})),
        assistant(("Bash", {"command": QUOTE})),
    ]
    run = load_module().parse_run(lines)
    assert run.bash_commands == ["sc broker quote --help", QUOTE]
    assert run.web_fetches == ["https://github.com/x"]
    assert run.mcp_tools == ["mcp__claude_ai_Scalable__quote"]


def test_hit_needs_help_before_quote():
    module = load_module()
    assert module.is_hit(module.Run(["python -I /x/check_install.py", "sc broker quote --help", QUOTE], []))
    assert module.is_hit(module.Run(["sc capabilities --json", "sc broker quote --json --isin IE00B4L5Y983"], []))
    assert module.is_hit(module.Run(["sc help broker quote && " + QUOTE], []))
    assert not module.is_hit(module.Run([QUOTE], []))
    assert not module.is_hit(module.Run([QUOTE, "sc broker quote --help"], []))


def test_quote_needs_isin_and_json():
    module = load_module()
    assert not module.is_hit(module.Run(["sc broker quote --help", "sc broker quote --isin IE00B4L5Y983"], []))
    assert not module.is_hit(module.Run(["sc broker quote --help", "sc broker quote --isin DE0001 --json"], []))


def test_web_fetch_or_mcp_fails_a_run():
    module = load_module()
    commands = ["sc broker quote --help", QUOTE]
    assert not module.is_hit(module.Run(commands, [], ["https://github.com/x"]))
    assert not module.is_hit(module.Run(commands, ["mcp__claude_ai_Scalable__quote"]))
