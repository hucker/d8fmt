import datetime
import pytest
from src.d8fmt import transform_format,CANONICAL,is_zone_free


@pytest.mark.parametrize("input_format, expected_output", [

    # Day of Year
    ("305", "%j"),  # Day of the year (October 31 is the 304th day of 2004)

    # Year and month
    ("2004", "%Y"),  # Year
    ("10", "%m"),  # Month number
    ("October", "%B"),  # Full month name
    ("Oct", "%b"),  # Abbreviated month name

    # Day
    ("31", "%d"),  # Day of the month
    ("Sunday", "%A"),  # Full weekday name
    ("Sun", "%a"),  # Abbreviated weekday name

    # Time (hour, minute, second)
    ("13", "%H"),  # 24-hour format hour
    ("01", "%I"),  # 12-hour format hour
    ("12", "%M"),  # Minutes
    ("11", "%S"),  # Seconds
    ("PM", "%p"),  # AM/PM marker

    # Microseconds
    (".000000", ".%f"),  # Fractional seconds

    # Week numbers
    ("43", "%W"),  # Week of year (starting with Sunday)
    ("44", "%U"),  # Week of year (starting with Monday)
])
def test_transform_format(input_format, expected_output):
    actual_output = transform_format(input_format)
    assert actual_output == expected_output

    # Round-trip: format the CANONICAL date using the resulting format
    formatted_date = CANONICAL.strftime(actual_output)
    assert formatted_date == input_format

@pytest.mark.parametrize("input_format, expected_format", [

    # Week-based formats
    ("2004-W43-0", "%Y-W%W-%w"),  # ISO week-based format (Start Sunday 0-6 )
    ("2004-W44-7", "%Y-W%U-%u"),  # ISO week-based format (Start Monday 1-7 )

    # US-style date formats
    ("10-31-2004 13:12:11", "%m-%d-%Y %H:%M:%S"),  # Month-Day-Year + 24-hour time
    ("10/31/2004 01:12:11 PM", "%m/%d/%Y %I:%M:%S %p"),  # Month/Day/Year + 12-hour time with AM/PM

    # ISO-8601 full date and time
    ("2004-10-31 13:12:11", "%Y-%m-%d %H:%M:%S"),
    ("2004-10-31T13:12:11", "%Y-%m-%dT%H:%M:%S"),  # ISO format with 'T' separator

    # European-style date formats
    ("31/10/2004 13:12:11", "%d/%m/%Y %H:%M:%S"),  # Day/Month/Year + 24-hour time
    ("31-10-2004 01:12:11 PM", "%d-%m-%Y %I:%M:%S %p"),  # Day-Month-Year + 12-hour time with AM/PM

    # Long-form formats
    ("Sunday, October 31, 2004 13:12:11", "%A, %B %d, %Y %H:%M:%S"),  # Full weekday and month names
    ("Sun, Oct 31, 2004 01:12:11 PM", "%a, %b %d, %Y %I:%M:%S %p"),  # Abbreviated weekday and month names

    # Date only
    ("2004-10-31", "%Y-%m-%d"),  # Standard ISO-8601 date
    ("31/10/2004", "%d/%m/%Y"),  # European-style date

    # Time only
    ("13:12:11", "%H:%M:%S"),  # 24-hour time
    ("01:12:11 PM", "%I:%M:%S %p"),  # 12-hour time with AM/PM

])
def test_transform_format_full_dates(input_format, expected_format):
    actual_format = transform_format(input_format)
    formatted_date = CANONICAL.strftime(actual_format)

    assert actual_format == expected_format

    # Round-trip: format the CANONICAL date using the resulting format
    assert formatted_date == input_format


# List of test cases with invalid date strings
@pytest.mark.parametrize("invalid_date_string", [
    # Cases where the timezone doesn't start with " +" or " -"
    "2004-10-31T13:12:11 +0530",  # Missing leading space before timezone
    "2004-10-31T13:12:11 -0800",  # Missing leading space before timezone

    # Cases with invalid timezone abbreviations
    "2004-10-31T13:12:11 PST",  # Unsupported abbreviation (PST)
    "2004-10-31T13:12:11 EST",  # Unsupported abbreviation (EST)
    "2004-10-31T13:12:11 CDT",  # Unsupported abbreviation (CDT)
    "2004-10-31T13:12:11 GMT",  # Unsupported abbreviation (GMT)

    # Cases with both invalid patterns and abbreviations
    "2004-10-31T13:12:11 -0530",  # No "+" or "-" for timezone offset
    "2004-10-31T13:12:11 +PDT",  # Leading space but invalid timezone abbreviation (PDT)
])
def test_is_zone_free_invalid_cases(invalid_date_string):
    with pytest.raises(ValueError):
        is_zone_free(invalid_date_string)  # Function to validate format
