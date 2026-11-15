import re
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent / "plugins" / "finance" / "skills" / "scalable-cli"
SKILL = (SKILL_DIR / "SKILL.md").read_text()
COMMANDS = (SKILL_DIR / "references" / "commands.md").read_text()
MANUAL_URL = "https://github.com/ScalableCapital/scalable-cli/blob/main/public-docs/commands.md"
LISTED = {"overview", "cash-breakdown", "holdings"}
BROKER_SUBCOMMAND = re.compile(r"\bsc broker ([a-z][a-z-]*)")


def section(text, title):
    """Return a '## ' section whose heading contains title, up to the next '## ' heading."""
    match = re.search(rf"^## [^\n]*{re.escape(title)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, f"no '## ... {title}' section"
    return match.group(0)


def test_read_data_names_exactly_the_three_listed_commands():
    read_data = section(SKILL, "Read data")
    assert set(BROKER_SUBCOMMAND.findall(read_data)) == LISTED


def test_each_listed_command_has_json_flag():
    read_data = section(SKILL, "Read data")
    for subcommand in LISTED:
        assert f"sc broker {subcommand} --json" in read_data


def test_commands_reference_names_no_other_broker_subcommand():
    assert set(BROKER_SUBCOMMAND.findall(COMMANDS)) <= LISTED


def test_manual_url_on_main_is_named():
    assert MANUAL_URL in SKILL or MANUAL_URL in COMMANDS


def test_getting_help_names_every_help_form():
    help_section = section(SKILL, "Getting help")
    for form in ["sc --help", "sc help <command>", "sc capabilities --json"]:
        assert form in help_section
    assert "sc <command> --help" in help_section or "sc <command> -h" in help_section


def test_getting_help_says_options_are_explained_in_their_command_help():
    help_section = section(SKILL, "Getting help")
    assert re.search(r"options?[^.]*explained in[^.]*command's help", help_section, re.I | re.S)


def test_getting_help_comes_before_the_manual_and_calls_it_a_fallback():
    help_section = section(SKILL, "Getting help")
    if MANUAL_URL in SKILL:
        assert SKILL.index(help_section) < SKILL.index(MANUAL_URL)
    assert "fallback" in help_section.lower()


def test_does_not_teach_undocumented_help_forms():
    assert not re.search(r"(?<![-\w])-help\b", SKILL)
    assert not re.search(r"--[a-z][a-z-]* --help", SKILL)
