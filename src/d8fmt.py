"""
Deterministic format from a canonical example.

Canonical instant (fixed):
  2005-07-04 13:08:09   (Monday, July 4)

Rules:
- Only exact tokens from the canonical instant are recognized.
- Literals are preserved.
- AM/PM and UTC are accepted case-insensitively for matching.
- Fractional seconds are encoded via %<N>f (custom), where N is count of zeros
  after the decimal in the example. Rendering uses zeros (not microseconds).
- Produced base directives are standard strftime/strptime (cross-platform).
"""


import datetime as dt
import re



CANONICAL: dt.datetime = dt.datetime(
    2005, 7, 4, 13, 8, 9,

)

def is_zone_free(fmt: str):
    # Regex to detect the pattern +/-dddd
    tz_offset_pattern = r"[+-]\d{4}"
    # List of invalid timezone strings
    invalid_timezones = ["PST", "EST", "CST", "MST", "AST", "HST", "AKST", "PDT", "EDT", "CDT", "MDT", "ADT", "HADT",
                         "AKDT"]

    # Check for +/-dddd offset
    if re.search(tz_offset_pattern, fmt):
        raise ValueError(f"Invalid format string: '{fmt}' contains unsupported +/-dddd patterns.")

    # Check for invalid timezone abbreviations
    for tz in invalid_timezones:
        if tz in fmt:
            raise ValueError(f"Invalid format string: '{fmt}' contains unsupported timezone abbreviation '{tz}'.")
    return True


def transform_format(fmt: str) -> str:
    # Replacement mapping.  Note we take advantage of
    # the diction being order so as we iterate over these items
    # they are going in the order we specifiy
    replacements = {
        ".000000": ".%f",  # Microseconds (truncated example)
        "2007": "%Y",  # Year (4-digit)
        "July": "%B",  # Full month name
        "JULY": "%B",  # Full month name
        "july": "%B",  # Full month name
        "Jul": "%b",  # Abbreviated month name
        "JUL": "%b",  # Abbreviated month name
        "jul": "%b",  # Abbreviated month name
        "Monday": "%A",  # Full weekday name
        "MONDAY": "%A",  # Full weekday name
        "monday": "%A",  # Full weekday name
        "MON": "%a",  # Abbreviated weekday name
        "Mon": "%a",  # Abbreviated weekday name
        "mon": "%a",  # Abbreviated weekday name
        "01": "%I",  # Hour (12-hour clock)
        "13": "%H",  # Hour (24-hour clock)
        "08": "%M", # Minute
        "AM": "%p",  # AM/PM marker
        "PM": "%p",  # AM/PM marker
        "09": "%S",  # Seconds
        "26": "%U",  # Week of the year (starting with Sunday)
        "27": "%W",  # Week of the year (starting with Monday)
        "05": "%y",  # Year (last 2 digits)
        "07": "%m",  # Month number
        "04": "%d",  # Day of the month
        "185": "%j",  # Day of the year
        #".000000": ".%f",  # Microseconds (truncated example)
        #".00000": ".%f" , # Microseconds (truncated example)
        #".0000": ".%f",  # Microseconds (truncated example)
        #".000": ".%f",  # Microseconds (truncated example)
        #".00": ".%f",  # Microseconds (truncated example)
        #".0": ".%f",  # Microseconds (truncated example)

        # These should not be here!
        #"1": "%m",
        #"7": "%m",
        #"4": "%d",
        #"5": '%y',
        #"9": '%S',
        #"8": "%M",
    }

    # Regex to detect the pattern
    pattern = r"[+-]\d{4}"

    is_zone_free(fmt)

    # Perform replacements using the mapping
    for key, value in replacements.items():
        fmt = fmt.replace(key, value)

    return fmt

