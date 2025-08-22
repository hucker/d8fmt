import sys

import pytest

from d8fmt import run_cli,make_d8fmt_parser


def test_default_arguments(monkeypatch, capsys):
    """
    Test the script with no arguments.
    The default format string should be used.
    """
    monkeypatch.setattr(sys, "argv", ["script.py", "-c"])  # Mock no arguments (just script name)
    with pytest.raises(SystemExit) as exc:  # Capture sys.exit call
        run_cli()  # Replace this with the function that executes argparse/CLI logic
    assert exc.value.code == 0  # Exit code should be 0
    captured = capsys.readouterr()  # Capture stdout/stderr
    assert "Sun Oct 31 13:12:11" in captured.out  # Example output check

def test_default_arguments(monkeypatch, capsys):
    """
    Test the script with no arguments.
    The default format string should be used.
    """
    monkeypatch.setattr(sys, "argv", ["script.py", "Sunday October 31 2004 13:12:11.000000","-c"])  # Mock no arguments (just script name)
    with pytest.raises(SystemExit) as exc:  # Capture sys.exit call
        run_cli()  # Replace this with the function that executes argparse/CLI logic
    assert exc.value.code == 0  # Exit code should be 0
    captured = capsys.readouterr()  # Capture stdout/stderr
    assert "Sunday October 31 2004 13:12:11.000000\n" in captured.out  # Example output check


def test_verbose_flag(monkeypatch, capsys):
    """
    Test the --canonical (-c) flag to ensure it uses the canonical datetime.
    """
    monkeypatch.setattr(sys, "argv", ["script.py", "-c", "-v"])
    with pytest.raises(SystemExit) as exc:
        run_cli()
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "Original Format String" in captured.out
    assert "Tokenized String" in captured.out
    assert "Formatted String" in captured.out
    assert "{DAY3} {MONTH3} {DAY#} {HOUR24}:{MINUTE}:{SECOND}" in captured.out
    assert "%a %b %d %H:%M:%S" in captured.out
    assert "Sun Oct 31 13:12:11" in captured.out  # Canonical datetime should appear in output


def test_unmatched_brace(monkeypatch, capsys):
    """
    Test that an unmatched '{' in the format string causes an unexpected error.
    """
    args = ["script.py", "{YEAR4}-{MONTH3}-{DAY# {HOUR24}:{MINUTE}:{SECOND}"]
    monkeypatch.setattr(sys, "argv", args)
    with pytest.raises(SystemExit) as exc:  # Catch the sys.exit call
        run_cli()  # Replace with your script's main function if applicable
    assert exc.value.code == 2  # Ensure exit code is 2 for unexpected errors
    captured = capsys.readouterr()
    assert "unexpected '{' in field name" in captured.err  # Ensure the error message is printed to stderr


def test_unknown_var(monkeypatch, capsys):
    """
    Test that an unknown variable '{FOOBAR}' exits
    """
    monkeypatch.setattr(sys, "argv", ["script.py", "{FOOBAR}"])
    with pytest.raises(SystemExit) as exc:  # Catch the sys.exit call
        run_cli()  # Replace with your script's main function if applicable
    assert exc.value.code == 1  # Ensure exit code is 2 for unexpected errors
    captured = capsys.readouterr()
    assert "Missing macro in fmt string" in captured.err  # Ensure the error message is printed to stderr


def test_canonical_formatting(monkeypatch, capsys):
    """
    Tests the command-line script's ability to handle --canonical mode, ensuring
    proper processing of input format strings, tokenization, and output formatting.
    """

    # Input format string and expected outputs
    format_string = "{YEAR4}-{MONTH#}-{DAY#} {HOUR12}:{MINUTE}:{SECOND} {AM}"
    expected_tokenized = "%Y-%m-%d %I:%M:%S %p"  # Expected tokenized string
    expected_formatted = "2004-10-31 01:12:11 AM"  # Expected formatted string

    # Mock the command-line arguments as if they were passed to the script
    monkeypatch.setattr(sys, "argv", ["d8fmt.py", "--canonical", format_string])

    # Mock sys.exit to prevent it from terminating the test process
    monkeypatch.setattr(sys, "exit", lambda x: None)

    # Run the CLI entry point function
    run_cli()

    # Capture the output from stdout
    captured = capsys.readouterr()
    output = captured.out

    # Assertions: verify all stages are present in the output
    assert output == "2004-10-31 01:12:11 PM\n"


def test_all_flag(monkeypatch, capsys):
    """
    Tests the command-line script's ability to handle --canonical mode, ensuring
    proper processing of input format strings, tokenization, and output formatting.
    """

    # Mock the command-line arguments as if they were passed to the script
    monkeypatch.setattr(sys, "argv", ["d8fmt.py", "--canonical", "--all"])

    # Mock sys.exit to prevent it from terminating the test process
    monkeypatch.setattr(sys, "exit", lambda x: None)

    # Run the CLI entry point function
    run_cli()

    # Capture the output from stdout
    captured = capsys.readouterr()
    output = captured.out

    # Assertions: verify all stages are present in the output
    assert output.startswith(
        "day=Sunday Sun 31 mon=October Oct 10 y=04 2004 hr=01PM/13 min=12 s=11.000000 DOY=305 WeekOfYear=44 WeakOfYearIso=43 WDAY#=0 WDAY#ISO=7")

@pytest.mark.parametrize(
    "cli_args,expected_results",
    [
        # Test case 1: Canonical flag and default format
        (["-c"], {
            "canonical": True,
            "all": False,
            "verbose": False,
            "format_string": "{DAY3} {MONTH3} {DAY#} {HOUR24}:{MINUTE}:{SECOND}",
        }),

        # Test case 2: `--all` flag with custom format
        (["-a", "{HOUR12}:{MINUTE}"], {
            "canonical": False,
            "all": True,
            "verbose": False,
            "format_string": "{HOUR12}:{MINUTE}",
        }),

        # Test case 3: Canonical and `--all` flags with custom format
        (["-c", "-a", "{HOUR12}:{MINUTE}"], {
            "canonical": True,
            "all": True,
            "verbose": False,
            "format_string": "{HOUR12}:{MINUTE}",
        }),

        # Test case 4: Verbose flag with default format
        (["-v"], {
            "canonical": False,
            "all": False,
            "verbose": True,
            "format_string": "{DAY3} {MONTH3} {DAY#} {HOUR24}:{MINUTE}:{SECOND}",
        }),

        # Test case 5: Default behavior with no arguments
        ([], {
            "canonical": False,
            "all": False,
            "verbose": False,
            "format_string": "{DAY3} {MONTH3} {DAY#} {HOUR24}:{MINUTE}:{SECOND}",
        }),

        # Test case 6: Canonical flag with verbose output
        (["-c", "-v"], {
            "canonical": True,
            "all": False,
            "verbose": True,
            "format_string": "{DAY3} {MONTH3} {DAY#} {HOUR24}:{MINUTE}:{SECOND}",
        }),

        # Test case 7: Custom format string only
        (["{HOUR12}:{MINUTE} {AM}"], {
            "canonical": False,
            "all": False,
            "verbose": False,
            "format_string": "{HOUR12}:{MINUTE} {AM}",
        }),
    ],
)
def test_make_d8fmt_parser(cli_args, expected_results):
    """
    Parameterized test for make_d8fmt_parser() to ensure all CLI options are parsed correctly.
    """
    parser = make_d8fmt_parser()
    args = parser.parse_args(cli_args)

    # Assert all options match expected results
    for key, expected_value in expected_results.items():
        assert getattr(args, key) == expected_value
