"""
Constants and Lookup Tables for Date and Time Formatting.

This module defines constants and lookup tables used for replacing custom placeholders with
corresponding Python `datetime` format specifiers. These constants are essential for the
`ezftime` formatting functionality, allowing convenient mapping of human-readable macros
(e.g., `{HOUR12}`) to standard datetime formatting directives (e.g., `%I`).

### Constants:
- **CANONICAL_DATE** (`datetime.datetime`): A predefined canonical datetime value set to
  October 31, 2004, at 13:12:11 UTC.

### Lookup Tables:
1. **MACRO_LOOKUP_TABLE**:
   - Maps custom placeholders (e.g., `HOUR12`, `MONTH`, etc.) to their corresponding Python
     `strftime` format codes (e.g., `%I`, `%B`, etc.).
   - The dictionary is ordered to ensure specific mappings are processed in a precise order.

2. **DATETIME_LOOKUP_TABLE**:
   - Maps specific literal strings (e.g., `"October"`, `"Sun"`, `"305"`) to their corresponding
     `strftime` format codes (e.g., `%B`, `%a`, `%j`).
   - Provides extended matching for variations such as different capitalizations of month and
     weekday names.
   - Helps in parsing specific datetime values from text or custom formats.

### Notes:
- The dictionaries take advantage of Python's ordered nature (from version 3.7+) to ensure
  replacement order is predictable.
- The **DATETIME_LOOKUP_TABLE** includes additional mappings for specific edge cases, such as
  week numbers, fractional seconds, and ISO-based weekdays.
- Care should be taken when working with keys like `"0"` and `"7"`, as their mappings (`%w`
  and `%u`) might behave differently depending on the context.

### Example Usage:
1. Replace a `{HOUR12}` macro with `%I` using the `MACRO_LOOKUP_TABLE`.
2. Parse `"Sunday"` into `%A` using the `DATETIME_LOOKUP_TABLE`.

These constants and tables provide the foundation for datetime-related formatting and macro
substitution in the library.
"""
import datetime as dt

CANONICAL_DATE: dt.datetime = dt.datetime(

    2004, 10, 31, 13, 12, 11, tzinfo=dt.timezone.utc
)

"""
MACRO_LOOKUP_TABLE

A dictionary mapping custom placeholder macros to Python's `strftime` format specifiers
used for date and time formatting.

This table defines a higher-level, human-readable macros (e.g., "DAY" for the full weekday name)
that can be replaced with their corresponding lower-level `strftime` directives (e.g., "%A").
These macros are utilized in formatting functions, such as `ez_format`, to dynamically format
datetime strings in a more expressive and readable way.

Key Concepts:
- The dictionary is **ordered**, ensuring that replacements occur in the specified order,
  which is particularly important if there are overlapping keys (e.g., "AM" and "PM").
- This abstraction enables easy customization and extension of datetime formatting behavior.

Key-Value Mapping Example:
- "DAY" → "%A" (e.g., "Monday")
- "MONTH3" → "%b" (e.g., "Oct")
- "HOUR24" → "%H" (e.g., "15" for 3 PM in 24-hour format)

Attributes:
    HOUR12: Hour (12-hour clock, zero-padded) [01 to 12]
    HOUR24: Hour (24-hour clock, zero-padded) [00 to 23]
    MINUTE: Minute within the hour, zero-padded [00 to 59]
    SECOND: Seconds within the minute, zero-padded [00 to 59]
    MICROSEC: Microsecond value, zero-padded to 6 digits [000000 to 999999]
    MONTH: Full name of the month [e.g., October]
    MONTH3: Abbreviated month name [e.g., Oct]
    DAY: Full weekday name [e.g., Monday]
    DAY3: Abbreviated weekday name [e.g., Mon]
    AM/PM: Ante/Post-Meridiem marker (AM/PM)

Usage Example:
    >>> MACRO_LOOKUP_TABLE["HOUR12"]
    '%I'

    >>> MACRO_LOOKUP_TABLE["AM"]
    '%p'
"""
MACRO_LOOKUP_TABLE = {
    # Hour-related macros
    "HOUR12": "%I",  # Hour (12-hour clock, zero-padded) [01, 02, ... 12]
    "HOUR24": "%H",  # Hour (24-hour clock, zero-padded) [00, 01, ... 23]
    "HOUR": "%I",  # Alias for "HOUR12"; hour on a 12-hour clock

    # Minute and second macros
    "MINUTE": "%M",  # Minute (zero-padded) [00, 01, ... 59]
    "SECOND": "%S",  # Second (zero-padded) [00, 01, ... 59]
    "MICROSEC": "%f",  # Microsecond (zero-padded to 6 digits) [000000, ... 999999]

    # Date and time period macros
    "AM": "%p",  # AM/PM marker (e.g., "AM" or "PM")
    "PM": "%p",  # Alias for AM/PM marker

    # Day-related macros
    "DAY": "%A",  # Full weekday name (e.g., "Monday")
    "DAY3": "%a",  # Abbreviated weekday name (e.g., "Mon")
    "DAY#": "%d",  # Day of the month (zero-padded) [01, 02, ... 31]

    # Week-related macros
    "WOY": "%U",  # Week of the year (starting with Sunday) [00-53]
    "WOYISO": "%W",  # Week of the year (starting with Monday) [00-53]
    "WDAY#ISO": "%u",  # ISO weekday as a number (1 for Monday, 7 for Sunday)
    "WDAY#": "%w",  # Weekday as a number (0 for Sunday, 6 for Saturday)

    # Month-related macros
    "MONTH": "%B",  # Full month name (e.g., "October")
    "MONTH3": "%b",  # Abbreviated month name (e.g., "Oct")
    "MONTH#": "%m",  # Month as a zero-padded number [01, 02, ... 12]

    # Year-related macros
    "YEAR2": "%y",  # Year without century (zero-padded) [00, 01, ... 99]
    "YEAR4": "%Y",  # Year with century (e.g., "2023")

    # Day-of-year macro
    "DOY": "%j",  # Day of the year as a zero-padded number [001, 002, ... 366]

    # Time zone and locale macros
    "TZ": "%Z",  # Time zone name (e.g., "UTC", "PST", or empty if not applicable)
    "UTCOFF": "%z",  # UTC offset in the form `+HHMM` or `-HHMM`
    "LOCALE": "%x",  # Locale’s representation of date (e.g., "10/31/04" in the US)
}


DATETIME_LOOKUP_TABLE = {
    ".000000": ".%f",  # Microseconds (truncated example)
    "2004": "%Y",  # Year (4-digit)
    "305": "%j",  # Day of the year
    "October": "%B",  # Full month name
    "OCTOBER": "%B",  # Full month name
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
