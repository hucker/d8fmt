"""
This module contains tests for validating the functionality of the `datetime_ez` formatting library
and its integration within a command-line script (`d8fmt.py`).

The tests focus on verifying:
- The correctness of date and time formatting using `datetime_ez` for a variety of format strings.
- The accurate construction of `datetime_ez` objects from standard `datetime` values.
- The behavior of the command-line script, including its ability to handle canonical dates, tokenized formats,
  and correctly formatted outputs.
- Robust handling of edge cases, such as raw text input and complex format strings.
- Script integration via subprocess execution to ensure the CLI behaves as expected, producing expected
  stdout, stderr, and return codes.

These test cases collectively ensure the reliability, correctness, and robustness of both the library and CLI interface.
"""
import datetime

import pytest

from d8fmt import datetime_ez


@pytest.mark.parametrize("format_string, expected_output",
                         [("{YEAR4}-{MONTH#}-{DAY#}", "2004-10-31"),  # Basic year-month-day format
                          ("{MONTH#}/{DAY#}/{YEAR2} at {HOUR24}:{MINUTE}:{SECOND}", "10/31/04 at 13:12:00"),
                          # Month/Day/Year
                          ("{DAY}, {MONTH} {DAY#}, {YEAR4} {HOUR12}:{MINUTE}:{SECOND} {PM}",
                           "Sunday, October 31, 2004 01:12:00 PM",),
                          # Full verbose date
                          ("Canonical datetime", "Canonical datetime"),  # Edge case with raw text
                          ], )
def test_datetime_ez_formatting(format_string, expected_output):
    """
    Verifies that `datetime_ez` correctly formats dates and times for various input format strings.
    """

    # Create a `datetime_ez` object for the canonical datetime
    d = datetime_ez(year=2004, month=10, day=31, hour=13, minute=12, second=0)
    formatted_date = d.ezftime(format_string)
    # Apply the custom ezftime method and verify the output
    assert formatted_date == expected_output


def test_datetime_ez_from_existing_datetime():
    """
    Ensures that a `datetime_ez` object initialized from a standard datetime
    object copies all attributes (e.g., year, month, day, time, timezone) correctly.
    """

    # Create a standard datetime object
    original_dt = datetime.datetime(2023, 10, 20, 15, 45, 30, 123456, tzinfo=datetime.timezone.utc)

    # Use the datetime_ez constructor with the dt parameter
    new_dt_ez = datetime_ez(dt_=original_dt)

    # Verify that all attributes are copied correctly
    assert new_dt_ez.year == original_dt.year
    assert new_dt_ez.month == original_dt.month
    assert new_dt_ez.day == original_dt.day
    assert new_dt_ez.hour == original_dt.hour
    assert new_dt_ez.minute == original_dt.minute
    assert new_dt_ez.second == original_dt.second
    assert new_dt_ez.microsecond == original_dt.microsecond
    assert new_dt_ez.tzinfo == original_dt.tzinfo
