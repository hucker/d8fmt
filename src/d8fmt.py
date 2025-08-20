"""
This module converts a canonical datetime example into a deterministic format string
based on standard `strftime`/`strptime` directives, while imposing strict rules
for tokens, literals, fractional seconds, and time zones.

Canonical Instant (Fixed):
  - `2004-10-31 13:12:11` is used as a reference to validate and transform formats.

Rules:
  - Only tokens present in the canonical instant are allowed for formatting.
  - Literals in the format strings are preserved as is.
  - Time zones are strictly validated:
  - Timezone abbreviations (e.g., PST, GMT) are explicitly prohibited.
  - Fractional seconds:
    - Always render fractional seconds with zero padding.
  - The output format uses cross-platform `strftime`/`strptime` directives.
  - Token replacement uses an ordered mapping to ensure correctness.

Functions:
  - `is_zone_free(fmt: str) -> bool`:
    Validates the absence of unsupported timezone formats, offsets, or abbreviations.

  - `snap_fmt(fmt: str) -> str`:
    Converts a format string using token replacement based on the canonical instant.
    Enforces all rules, validates timezones, and maps tokens into corresponding strftime directives.

Mapping Example:
  - `"2004"` → `"%Y"`:  Year (4-digit)
  - `"31"` → `"%d"`: Day of the month
  - `"October"` → `"%B"`: Full month name
  - `"13"` → `"%H"`: Hour (24-hour clock)
  - `PM` -> '%p' AM/PM marker
  - `".000000"` → `"%f"`: Microseconds
  - `"0"` → `"%w"`: Day of the week (Sunday = 0, Saturday = 6 non-ISO)
  - `"7"` → `"%u"`: Day of the week (ISO, Monday = 1, Sunday = 7)
  - `"AM/PM"` → `"%p"`: AM/PM marker

Error Handling:
  - Raises a `ValueError` if invalid timezone formats or abbreviations are detected.
"""

import datetime as dt
import re



CANONICAL: dt.datetime = dt.datetime(
    2004, 10, 31, 13, 12, 11,tzinfo=dt.timezone.utc
)

# Replacement mapping.  Note we take advantage of
# the diction being order so as we iterate over these items
# they are going in the order we specifiy
DATETIME_LOOKUP_TABLE = {
    "{HOUR12}": "%I",
    "{HOUR24}": "%H",
    '{DOY}': "%j",
    "{YEAR2}": "%y",
    "{YEAR4}": "%Y",
    "{MONTH}": "%B",
    "{MONTH3}": "%b",
    "{MONTH#}": "%m",
    "{DAY}": "%A",
    "{DAY3}": "%a",
    "{DAY#}": "%d",
    "{HOUR}": "%I",
    "{MINUTE}": "%M",
    "{SECOND}": "%S",
    "{MICROSEC}": "%f",
    "{AM}": "%p",
    "{PM}": "%p",
    "{WOY}": "%U",
    "{WOYISO}": "%W",
    "{WDAY#ISO}": "%u",
    "{WDAY#}": "%w",
    "{TZ}": "%Z",
    "{UTCOFF}": "%z",
    "{LOCALE}":"%x",

    ".000000": ".%f",  # Microseconds (truncated example)
    "2004": "%Y",  # Year (4-digit)
    "305": "%j",  # Day of the year
    "October": "%B",  # Full month name
    "OCTOBER": "%B",  # Full month name
    "October": "%B",  # Full month name
    "october": "%B",  # Full month name
    "Oct": "%b",  # Abbreviated month name
    "OCT": "%b",  # Abbreviated month name
    "oct": "%b",  # Abbreviated month name
    "Sunday": "%A",  # Full weekday name
    "SUNDAY": "%A",  # Full weekday name
    "sunday": "%A",  # Full weekday name
    "SUN": "%a",  # Abbreviated weekday name
    "Sun": "%a",  # Abbreviated weekday name
    "sun": "%a",  # Abbreviated weekday name
    "01": "%I",  # Hour (12-hour clock)
    "04": "%y",  # Year (last 2 digits)
    "10": "%m",  # Month number
    "11": "%S",  # Seconds
    "12": "%M",  # Minute
    "13": "%H",  # Hour (24-hour clock)
    "31": "%d",  # Day of the month
    "44": "%U",  # Week of the year (starting with Sunday)
    "43": "%W",  # Week of the year (starting with Monday)
    "AM": "%p",  # AM/PM marker
    "PM": "%p",  # AM/PM marker
    "am": "%p",  # AM/PM marker
    "pm": "%p",  # AM/PM marker
    # ".000000": ".%f",  # Microseconds (truncated example)
    # ".00000": ".%f" , # Microseconds (truncated example)
    # ".0000": ".%f",  # Microseconds (truncated example)
    # ".000": ".%f",  # Microseconds (truncated example)
    # ".00": ".%f",  # Microseconds (truncated example)
    # ".0": ".%f",  # Microseconds (truncated example)

    # These will be problematic
    "0": "%w",  # 0th day of week ( 0-6)
    "7": "%u",  # 7th day of week (ISO 1-7)
}

def is_zone_free(fmt: str):
    # Regex to detect the pattern +/-dddd
    tz_offset_pattern = r" [+-]\d{4}"
    # List of invalid timezone strings
    invalid_timezones = ["PST", "EST", "CST", "MST", "AST", "HST", "AKST", "PDT", "EDT", "CDT", "MDT", "ADT", "HADT",
                         "AKDT","GMT"]

    # Check for +/-dddd offset
    if re.search(tz_offset_pattern, fmt):
        raise ValueError(f"Invalid format string: '{fmt}' contains unsupported +/-dddd patterns.")

    # Check for invalid timezone abbreviations
    for tz in invalid_timezones:
        if tz in fmt:
            raise ValueError(f"Invalid format string: '{fmt}' contains unsupported timezone abbreviation '{tz}'.")
    return True


def snap_fmt(fmt: str,replacments:dict[str,str]|None = None) -> str:

    replacements = replacments or DATETIME_LOOKUP_TABLE

    # Regex to detect the pattern
    pattern = r"[+-]\d{4}"

    is_zone_free(fmt)

    # Perform replacements using the mapping
    for key, value in replacements.items():
        fmt = fmt.replace(key, value)

    return fmt


class datetime_snap(dt.datetime):
    def stezftime(self, fmt: str) -> str:
        """
        Provide a format string using the cannonical instant to transform
        and apply to the datetime object.  The time you should format to is
        October 31, 2004 13:12:11.000000

        Just use standard time formatting so you can just use the string

        "10/31/2004 13:12:11"
        "Oct-31-2004 01:12:11 PM"
        "Sunday, October 31, 2004 13:12:11 PM"

        For completeness lesser used unique values for date-time formatting are:

        44  Week of the year (starting with Sunday)
        43  Week of the year (starting with Monday)
        305  Day of the year
        0 Day of the week (0-6)
        7 Day of week (ISO 1-7)

        Which means this will work:

        "Sunday, October 31, 2004 13:12:11 PM Week-44 Day-305 DayOfWeek=7"

        Any of these format strings will do the right thing.  The only thing
        you must make sure about is that the format string should only be used
        for date time parts and common separators.  You can add arbitrary text
        but that text might collide with the date time parts.  Ideally you
        would make a date string and insert that into another string.

        """
        transformed_fmt = snap_fmt(fmt)
        return self.strftime(transformed_fmt)

