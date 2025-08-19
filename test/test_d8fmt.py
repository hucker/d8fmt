# test_datetime_infer.py
import datetime as dt
import pytest
from src.d8fmt import transform_format,is_zone_free,CANONICAL


@pytest.mark.parametrize("input_format,expected_output", [

    # 14. Week of the year (based on Sunday) and year (YYYY-W)
    ("2005-26", "%Y-%U"),

    # 15. Week of the year (based on Monday) and year (YYYY-W)
    ("2005-27", "%Y-%W"),

    # 1. Basic ISO 8601 date format (YYYY-MM-DD HH:MM:SS)
    ("2005-07-04 13:08:09", "%Y-%m-%d %H:%M:%S"),

    # 2. Date only (YYYY-MM-DD)
    ("2005-07-04", "%Y-%m-%d"),

    # 3. Time only (HH:MM:SS)
    ("13:08:09", "%H:%M:%S"),

    # 4. Month name, Day, Year (Month DD, YYYY)
    ("July 04, 2005", "%B %d, %Y"),

    # 5. Abbreviated Month and Day (Mon DD, YYYY)
    ("Jul 04, 2005", "%b %d, %Y"),

    # 6. Year with last 2 digits (YY-MM-DD)
    ("05-07-04", "%y-%m-%d"),

    # 7. Full weekday name (Weekday, Month DD, YYYY)
    ("Monday, July 04, 2005", "%A, %B %d, %Y"),

    # 8. Abbreviated weekday name (AbbrWeekday, Month DD, YYYY)
    ("Mon, Jul 04, 2005", "%a, %b %d, %Y"),

    # 9. Day of Year (YYYY-DDD)
    ("2005-185", "%Y-%j"),

    # 10. Day and 12-hour clock with period (HH:MM:SS AM/PM)
    ("01:08:09 PM", "%I:%M:%S %p"),

    # 11. Packed Date and Time without separators (YYYYMMDDHHMMSS)
    ("20050704130809", "%Y%m%d%H%M%S"),

    # 12. Packed Date only without separators (YYYYMMDD)
    ("20050704", "%Y%m%d"),

    # 13. Packed Time only without separators (HHMMSS)
    ("130809", "%H%M%S"),



    # 16. Simple fractional seconds (HH:MM:SS.mmm)
    ("13:08:09.000000", "%H:%M:%S.%f"),

    # 17. Literals like "at" with time (YYYY-MM-DD at HH:MM:SS)
    ("2005-07-04 at 13:08:09", "%Y-%m-%d at %H:%M:%S"),

    # 18. Literal text (e.g., "Time is 13:08:09")
    ("Time is 13:08:09", "Time is %H:%M:%S"),

    # 19. Combining textual month and day (Month DD HH:MM)
    ("July 04 13:08", "%B %d %H:%M"),

    # 20. Packed ISO DateTime with "T" separator (YYYYMMDDTHHMMSS)
    ("20050704T130809", "%Y%m%dT%H%M%S"),
    # 1. Packed Date Only (YYYYMMDD)
    ("20050704", "%Y%m%d"),

    # 2. Packed Date (YYMMDD)
    ("050704", "%y%m%d"),

    # 3. Packed Date (MMDDYYYY)
    ("07042005", "%m%d%Y"),

    # 4. Packed Time Only (HHMMSS)
    ("130809", "%H%M%S"),

    # 5. Packed Time with Hour and Minute (HHMM)
    ("1308", "%H%M"),

    # 6. Packed 12-Hour Clock With AM/PM (HHMMPM/AM)
    ("010809PM", "%I%M%S%p"),

    # 7. Packed Date and Time (YYYYMMDDHHMMSS)
    ("20050704130809", "%Y%m%d%H%M%S"),

    # 8. Packed Date and Time (YYMMDDHHMMSS)
    ("050704130809", "%y%m%d%H%M%S"),

    # 9. Packed Date and Time, Month First (MMDDYYYYHHMMSS)
    ("07042005130809", "%m%d%Y%H%M%S"),

    # 10. Packed ISO DateTime with "T" Separator (YYYYMMDDTHHMMSS)
    ("20050704T130809", "%Y%m%dT%H%M%S"),

    # 11. Packed ISO DateTime with "T" Separator (YYMMDDTHHMMSS)
    ("050704T130809", "%y%m%dT%H%M%S"),

    # 12. Packed Date and Day of Year (YYYYDDD)
    ("2005185", "%Y%j"),

    # 13. Packed Date and Day of Year (YYDDD)
    ("05185", "%y%j"),

    # 14. Packed Week-Based Date (Year + Week + Day) (YYYYWWDD)
    ("20052704", "%Y%W%d"),

    # 15. Packed Week-Based Date (Year + Week# + Day) (YYWWD)
    ("052601", "%y%U%I"),

    # 16. Packed Year and Day of Year Representation (YYYYDDD)
    ("2005185", "%Y%j"),  # Day 185 of the year

    # 17. Packed Date Only with Abbreviated Year (YYMMDD)
    ("050704", "%y%m%d"),

    # 18. Packed Hour and Minute Only (HMM)
    ("0108", "%I%M"),  # Single digits for hour and minute
    ("1308", "%H%M"),  # Single digits for hour and minute

    # 19. Packed Time with Fractional Seconds (HHMMSS.mmm)
    ("130809.000000", "%H%M%S.%f"),

    # 20. Packed Date and Time with Fractional Seconds (YYYYMMDDHHMMSS.mmm)
    ("20050704130809.000000", "%Y%m%d%H%M%S.%f"),

])
def test_transform_format(input_format, expected_output):
    actual_output = transform_format(input_format)
    assert actual_output == expected_output
    # Round-trip test: use the format string to format the canonical_date
    formatted_date = CANONICAL.strftime(actual_output)

    # Compare the formatted string with the original input
    assert formatted_date == input_format


# Test cases for invalid inputs (containing timezones or offsets)
@pytest.mark.parametrize("invalid_format,expected_message", [
    # Cases with +/-dddd offsets
    ("2005-07-04 13:08+1200", "contains unsupported +/-dddd patterns"),  # Positive offset
    ("13:08-0930", "contains unsupported +/-dddd patterns"),  # Negative offset
    ("Schedule at 20050704+0800", "contains unsupported +/-dddd patterns"),  # Offset with packed date
    ("YYYY-MM-DDTHH:MM:SS-0500", "contains unsupported +/-dddd patterns"),  # ISO format with offset
    # Cases with invalid timezone abbreviations
    ("The time is 13:08 PST", "contains unsupported timezone abbreviation 'PST'"),  # PST abbreviation
    ("Event starts at 15:00 EST", "contains unsupported timezone abbreviation 'EST'"),  # EST abbreviation
    ("Date: 2005-07-04 CDT", "contains unsupported timezone abbreviation 'CDT'"),  # CDT abbreviation
    ("Midnight at 00:00 MST", "contains unsupported timezone abbreviation 'MST'"),  # MST abbreviation
    ("2005-07-04 HST", "contains unsupported timezone abbreviation 'HST'"),  # HST abbreviation
    ("Start 08:00 PDT", "contains unsupported timezone abbreviation 'PDT'"),  # PDT abbreviation
])
def test_is_zone_free_invalid_cases(invalid_format, expected_message):
    # Ensure the function raises ValueError for invalid formats
    with pytest.raises(ValueError):
        is_zone_free(invalid_format)
