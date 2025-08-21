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
import argparse
import sys


CANONICAL: dt.datetime = dt.datetime(
    2004, 10, 31, 13, 12, 11,tzinfo=dt.timezone.utc
)

# Replacement mapping.  Note we take advantage of
# the diction being order so as we iterate over these items
# they are going in the order we specifiy
MACRO_LOOKUP_TABLE = {
    "HOUR12": "%I",
    "HOUR24": "%H",
    'DOY': "%j",
    "YEAR2": "%y",
    "YEAR4": "%Y",
    "MONTH": "%B",
    "MONTH3": "%b",
    "MONTH#": "%m",
    "DAY": "%A",
    "DAY3": "%a",
    "DAY#": "%d",
    "HOUR": "%I",
    "MINUTE": "%M",
    "SECOND": "%S",
    "MICROSEC": "%f",
    "AM": "%p",
    "PM": "%p",
    "WOY": "%U",
    "WOYISO": "%W",
    "WDAY#ISO": "%u",
    "WDAY#": "%w",
    "TZ": "%Z",
    "UTCOFF": "%z",
    "LOCALE":"%x",
}

DATETIME_LOOKUP_TABLE = {
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
    """
    This is a placeholder. It will be replaced when timezones are supported.

    Throws exception if timezone formatting is detected.
    """
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


def ez_format(fmt: str,
              macros: dict[str, str] | None = None,
              replacements: [str, str] = None) -> str:
    """
    Formats a string by replacing placeholder macros with their corresponding values
    and applying additional datetime-based replacements.

    This function processes the input string `fmt` by performing a series of
    replacements:
      1. Replaces `{xxx}` macros using a provided or default mapping (`macros`).
      2. Applies further datetime-related replacements (`dt_replacements`) to
         format-specific placeholders.

    Args:
        fmt (str):
            The input format string containing placeholders to be replaced.
            Placeholders should match the keys in the mappings provided.

        macros (dict[str, str] | None, optional):
            A dictionary where keys represent macro placeholders (e.g., "{HOUR12}")
            and values represent their corresponding format tokens. If not provided,
            a default macro lookup table (`MACRO_LOOKUP_TABLE`) is used. The python
            str.format() syntax is used to format the string.

        replacements ([str, str], optional):
            A dictionary of additional canonical replacements for datetime format-specific
            placeholders (e.g., "%H", "%M"). If not provided, a default datetime
            lookup table (`DATETIME_LOOKUP_TABLE`) is used. The canonical instant is
            October 31, 2004 on a Sunday, at 13:12:11.000000. The weeks are 44 and 43.
            The day of year is 305. The days of the week are 0 and 7 respectively.

    Returns:
        str:
            The fully formatted string with all placeholder macros and datetime
            tokens replaced.

    Raises:
        ValueError: If the input string `fmt` contains invalid or unsupported
                    macros or formatting tokens not handled by the mappings.

    Examples:
        >>> ez_format("The time is {HOUR12}:{MINUTE} {AM}.",
                     macros={"HOUR12": "%I", "MINUTE": "%M", "AM": "%p"})
        'The time is %I:%M %p.'

        >>> ez_format("{YEAR4}-{MONTH#}-{DAY#}",
                     macros={"YEAR4": "%Y", "MONTH#": "%m", "DAY#": "%d"})
        '%Y-%m-%d'

        # With datetime replacements
        >>> ez_format("Today is {DAY}, {MONTH} {DAY#}, {YEAR4}.",
                     macros={"DAY": "%A", "MONTH": "%B", "DAY#": "%d", "YEAR4": "%Y"},
                     dt_replacements={"%A": "Monday", "%B": "October", "%d": "09", "%Y": "2023"})
        'Today is Monday, October 09, 2023.'

    Note:
        - The macro lookup table (`MACRO_LOOKUP_TABLE`) is expected to map keys like
          `"{HOUR12}"` to standard Python datetime format specifiers.
        - The order of operations ensures that all `{xxx}` macros are replaced first
          (via `format()` or manual replacement), followed by datetime token replacements.
    """

    macros = macros or MACRO_LOOKUP_TABLE
    replacements = replacements or DATETIME_LOOKUP_TABLE

    is_zone_free(fmt)

    # Use the .format to map all macros such as {DAY} and {MONTH} using format
    fmt = fmt.format(**macros)

    # Perform replacements using the mapping
    for key, value in replacements.items():
        fmt = fmt.replace(key, value)

    return fmt


class datetime_ez(dt.datetime):
    def __new__(cls, *args, dt=None, **kwargs):
        """
            Create a new instance of the `datetime_ez` class.

            This method overrides the standard `__new__` to provide additional functionality for creating an
            instance of `datetime_ez` from an existing `datetime` object using the `dt` parameter.
            If `dt` is provided, its attributes (such as `year`, `month`, `day`, etc.) are extracted and used to
            initialize the new instance. If `dt` is not provided, the method falls back to behaving as a standard
            `datetime` constructor and accepts the usual positional and keyword arguments (e.g., `year`, `month`,
            `day`, etc.).

            +----------------+------------------+------------------+
            | Placeholder    | Canonical Value | Macro            |
            +----------------+------------------+------------------+
            | %S             | 11              | {SECOND}         |
            | %M             | 12              | {MINUTE}         |
            | %H             | 13              | {HOUR24}         |
            | %I             | 01              | {HOUR12}         |
            | %d             | 31              | {DAY#}           |
            | %m             | 10              | {MONTH#}         |
            | %B             | October         | {MONTH}          |
            | %b             | Oct             | {MONTH3}         |
            | %Y             | 2004            | {YEAR4}          |
            | %y             | 04              | {YEAR2}          |
            | %A             | Sunday          | {DAY}            |
            | %a             | Sun             | {DAY3}           |
            | %w             | 0               | {WDAY#}          |
            | %u             | 7               | {WDAY#ISO}       |
            | %j             | 305             | {DOY}            |
            | %U             | 44              | {WOY}            |
            | %W             | 43              | {WOYISO}         |
            | %p             | AM/PM           | {AM}/{PM}        |
            | %Z             | (Timezone)      | {TZ}             |
            | %z             |                 | {UTCOFF}         |
            | %x             |                 | {LOCALE}         |
            | %f             | 000000          | {MICROSEC}       |


            ### Parameters:
            - `dt` (datetime, optional): An existing `datetime` object. If provided, the new `datetime_ez`
              object will be created using its attributes. Defaults to `None`.
            - `*args`: Positional arguments for creating a standard `datetime` object (used if `dt` is not provided).
            - `**kwargs`: Keyword arguments for creating a standard `datetime` object (used if `dt` is not provided).

            ### Returns:
            - `datetime_ez`: A new instance of the `datetime_ez` class, either initialized from the `dt` object
              or created using the provided positional and keyword arguments.

            ### Example Usage:
            **Create from a standard constructor:**
            ```python
            dt_ez = datetime_ez(2023, 10, 20, 15, 30, 45)
            print(dt_ez)  # 2023-10-20 15:30:45
            ```

            **Create from an existing datetime object:**
            ```python
            import datetime
            existing_dt = datetime.datetime(2023, 10, 20, 15, 30, 45)
            cloned_dt_ez = datetime_ez(dt=existing_dt)
            print(cloned_dt_ez)  # 2023-10-20 15:30:45
            ```
    """
        if dt:
            # Create new instance using the provided datetime object
            return super().__new__(
                cls,
                dt.year,
                dt.month,
                dt.day,
                dt.hour,
                dt.minute,
                dt.second,
                dt.microsecond,
                dt.tzinfo,  # Keep timezone if present
            )
        else:
            # Create new instance using regular datetime constructor
            return super().__new__(cls, *args, **kwargs)


    def ezftime(self, fmt: str) -> str:
        """
        Format a datetime object into a custom string using an enhanced set of macros for
        datetime components.

        ### Key Features:
        - You can use **standard Python datetime format strings** (e.g., `%Y`, `%m`, `%d`).
        - Additional **macros** such as `{HOUR12}`, `{MONTH}`, `{DAY}` offer flexibility
          and leverage a user-friendly style.
        - You can mix arbitrary text with datetime parts to create custom formats, but
          avoid conflicts where text resembles the placeholders.

        **Examples:**
        Quickly create formatted datetime strings with intuitive macros:
        - `"Today is {DAY}, {MONTH} {DAY#}, {YEAR4} at {HOUR12}:{MINUTE}:{SECOND} {AM}."`
          → `Sunday, October 31, 2004 at 01:12:11 PM`

        - `"Date: {MONTH#}/{DAY#}/{YEAR4}, Time: {HOUR24}:{MINUTE}."`
          → `Date: 10/31/2004, Time: 13:12`

        - `"Day {DOY} of the year {YEAR4}, Week {WOY}."`
          → `Day 305 of the year 2004, Week 44`



        ### Example Placeholders and Mappings:
        Here are some basic example mappings supported by this method:
        - `{YEAR4}` → `2004`
        - `{MONTH#}` → `10`
        - `{DAY}` → `Sunday`
        - `{HOUR24}` → `13`
        - `{HOUR12}` → `01`
        - `{SECOND}` → `11`
        - `{MICROSEC}` → `000000`
        - `{DOY}` → `305` (Day of the year)
        - `{WOY}` → `44` (Week of the year starting Sunday)

        ### Examples:
        Use these format strings to generate desired outputs:
        - `"Today is {DAY}, {MONTH} {DAY#}, {YEAR4} at {HOUR12}:{MINUTE}:{SECOND} {AM}."`
          → `Sunday, October 31, 2004 at 01:12:11 PM`

        - `"Date: {MONTH#}/{DAY#}/{YEAR4}, Time: {HOUR24}:{MINUTE}."`
          → `10/31/2004, Time: 13:12.`

        - `"Day {DOY} of the year {YEAR4}, Week {WOY}."`
          → `Day 305 of the year 2004, Week 44.`

        - `"Custom: <{YEAR4}-{MONTH#}-{DAY#} @ {HOUR24}:{MINUTE}>"`
          → `<2004-10-31 @ 13:12>`

        ### Supported Common Placeholders:
        - `{YEAR4}`: Four-digit year (e.g., `2004`).
        - `{YEAR2}`: Two-digit year (e.g., `04`).
        - `{MONTH}`: Full month (e.g., `October`).
        - `{MONTH3}`: Abbreviated month (e.g., `Oct`).
        - `{MONTH#}`: Month as a two-digit number (e.g., `10`).
        - `{DAY}`: Full day of the week (e.g., `Sunday`).
        - `{DAY3}`: Abbreviated day of the week (e.g., `Sun`).
        - `{DAY#}`: Day of the month as a two-digit number (e.g., `31`).
        - `{HOUR24}`: Hour in 24-hour format (e.g., `13`).
        - `{HOUR12}`: Hour in 12-hour format (e.g., `01`).
        - `{MINUTE}`: Minutes (e.g., `12`).
        - `{SECOND}`: Seconds (e.g., `11`).
        - `{MICROSEC}`: Microseconds (e.g., `000000`).
        - `{DOY}`: Day of the year (1-365 or 1-366 for leap years).
        - `{WOY}`: Week of the year starting on Sunday.

        ### Note to Users:
        To avoid conflicts, use simple text that does not overlap with placeholders
        (e.g., `{HOUR12}` or `%Y`). If you need to embed a datetime string into a
        larger text block, it’s recommended to format your date string separately
        before combining it with additional text.

        Returns:
            str: A fully formatted string containing the requested datetime.

        Examples:
        ```python
        snap = datetime_ez(2004, 10, 31, 13, 12, 11)

        # Example with macros
        snap.ezftime("Today is {DAY}, {MONTH} {DAY#}, {YEAR4} at {HOUR12}:{MINUTE}:{SECOND} {AM}.")
        # Output: "Today is Sunday, October 31, 2004 at 01:12:11 PM."

        # Traditional datetime formatting (no macros)
        snap.ezftime("%A, %B %d, %Y %H:%M:%S")
        # Output: "Sunday, October 31, 2004 13:12:11."

        # Mixing macros and datetime tokens (Not that you should do this)
        snap.ezftime("{YEAR4}-{MONTH#}-{DAY#} %H:%M")
        # Output: "2004-10-31 13:12"
        ```
        """
        return self.strftime(ez_format(fmt))

def run_cli():
    # Import here ONLY if we are running from command line.

    parser = argparse.ArgumentParser(description="Datetime formatter CLI")

    # Create the argument parser
    parser = argparse.ArgumentParser(
        description="Format a string using ezftime format specifiers and return appropriate exit codes."
    )
    parser.add_argument(
        "format_string",
        nargs="?",
        default="{DAY3} {MONTH3} {DAY#} {HOUR24}:{MINUTE}:{SECOND}",
        help=(
            "The format string to use, with ezftime placeholders (e.g., '{HOUR12}:{MINUTE} {AM}')."
            " If not provided, a default format will be used."
        ),
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help=("Use a format string that shows all replacements"),
    )
    parser.add_argument(
        "-c", "--canonical",
        action="store_true",
        help=(
            "Use the canonical datetime reference (October 31, 2004 13:12:11.000000) "
            "for formatting. If not provided, the current datetime is used."
        ),
    )
    parser.add_argument(
        "-o", "--print-original",
        action="store_true",
        help="Print the original format string provided as input.",
    )
    parser.add_argument(
        "-t", "--print-tokenized",
        action="store_true",
        help="Print the tokenized string after macro substitutions.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print everithing available for debugging purposes.",
    )

    try:
        args = parser.parse_args()
        if args.all:
            args.format_string = "day={DAY} {DAY3} {DAY#} mon={MONTH} {MONTH3} {MONTH#} y={YEAR2} {YEAR4} " \
                                 "hr={HOUR12}{PM}/{HOUR24} min={MINUTE} s={SECOND}.{MICROSEC} " \
                                 "DOY={DOY} WeekOfYear={WOY} WeakOfYearIso={WOYISO} " \
                                 "WDAY#={WDAY#} WDAY#ISO={WDAY#ISO} LOCALE={LOCALE}"

        # Determine the datetime to use
        if args.canonical:
            user_date = dt.datetime(2004, 10, 31, 13, 12, 11, 0)
        else:
            user_date = dt.datetime.now()

        # Tokenized format string (replace macros like {HOUR12} but leave datetime placeholders)
        tokenized_format = ez_format(args.format_string)

        # Final formatted string (apply formats)
        formatted_string = datetime_ez.ezftime(user_date, args.format_string)

        if args.verbose:
            args.print_original = True
            args.print_tokenized = True

        # Output controlled by flags
        if args.print_original:
            if args.verbose:
                print("Original Format String:")
            print(args.format_string)

        if args.print_tokenized:
            if args.verbose:
                print("\nTokenized String (with macros replaced):")
            print(tokenized_format)

        if args.verbose:
            print("\nFormatted String (with datetime values applied):")
        print(formatted_string)

        # If everything ran successfully, exit with status 0
        sys.exit(0)

    except KeyError as e:
        # If a macro is missing in the lookup table, handle gracefully
        print(f"Error: Missing macro in the format string - {e}", file=sys.stderr)
        sys.exit(1)  # Exit code 1 indicates general error

    except Exception as e:
        # Catch other unexpected errors
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)  # Use a different exit code for unexpected failures


if __name__ == "__main__": # pragma: no cover

    run_cli()
