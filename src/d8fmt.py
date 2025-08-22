"""
     d8fmt.py

     A module for handling advanced datetime formatting and parsing operations.

     Primary Components:
         Functions:
             - is_zone_free: Determines if a datetime string lacks time zone data.
             - ez_format: Formats datetime objects based on custom templates.
             - run_cli: Command-line interface for using the datetime utilities.

         Class:
             - datetime_ez: A specialized datetime class with extended functionality.

     Usage:
         - Import the module to use its utilities programmatically:
             from d8fmt import ez_format, is_zone_free
         - Execute the script to access the CLI:
             python d8fmt.py --help
     """


import argparse
import datetime as dt
import re
import sys

from .constants import DATETIME_LOOKUP_TABLE, MACRO_LOOKUP_TABLE


def is_zone_free(fmt: str):
    """
    Checks if the given datetime string is timezone-agnostic.

    Parameters:
       datetime_string (str): The datetime string to check.

    Returns:
       bool: True if the datetime string does not contain timezone information, False otherwise.

    """
    # Regex to detect the pattern +/-dddd
    tz_offset_pattern = r" [+-]\d{4}"
    # List of invalid timezone strings
    invalid_timezones = ["PST", "EST", "CST", "MST", "AST", "HST", "AKST", "PDT", "EDT",
                         "CDT", "MDT", "ADT", "HADT", "AKDT", "GMT"]

    # Check for +/-dddd offset
    if re.search(tz_offset_pattern, fmt):
        msg = f"Invalid format string: '{fmt}' contains unsupported +/-dddd patterns."
        raise ValueError(msg)

    # Check for invalid timezone abbreviations
    for tz in invalid_timezones:
        if tz in fmt:
            msg = f"Invalid format string: '{fmt}' contains unsupported timezone '{tz}'."
            raise ValueError(msg)
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
            October 31, 2004, on a Sunday, at 13:12:11.000000. The weeks are 44 and 43.
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
    """
    A subclass of `datetime.datetime` that provides enhanced functionality for human-readable and
    deterministic formatting of datetime objects.

    This class extends the standard `datetime` object by:
    - Allowing initialization from an existing `datetime` object via the `dt_` parameter.
    - Simplifying formatting with user-friendly macros through the `ezftime` method.

    ### Initialization:
    You can create a `datetime_ez` instance in two ways:
    - By providing a standard `datetime` object using the `dt_` parameter.
    - By using traditional positional and keyword arguments (e.g., `year`, `month`, `day`).

    ### Features:
    - Fully compatible with the base `datetime.datetime` methods and attributes.
    - Adds `ezftime`, a powerful formatting method, that supports both standard `strftime` tokens
      (e.g., `%Y`, `%m`, `%d`) and custom macros (e.g., `{HOUR12}`, `{MONTH#}`, `{DAY}`) as
      well as canonical format replacements.

    ### Parameters:
    - `dt_` (datetime, optional): An existing `datetime` object. If provided, the new `datetime_ez`
      object will clone its attributes. Defaults to `None`.
    - `*args`: Positional arguments for creating `datetime` object (used if `dt_` is not provided).
    - `**kwargs`: Keyword arguments for creating `datetime` object (used if `dt_` is not provided).

    ### Example Usage:
    #### Create from a standard constructor:
    ```python
    dt_ez = datetime_ez(2023, 10, 20, 15, 30, 45)
    print(dt_ez)  # 2023-10-20 15:30:45
    ```

    #### Create from an existing `datetime` object:
    ```python
    import datetime
    existing_dt = datetime.datetime(2023, 10, 20, 15, 30, 45)
    cloned_dt_ez = datetime_ez(dt_=existing_dt)
    print(cloned_dt_ez)  # 2023-10-20 15:30:45
    ```

    #### Use `ezftime` for formatting:
    ```python
    snap = datetime_ez(2004, 10, 31, 13, 12, 11)
    output = snap.ezftime("Today is {DAY}, {MONTH} {DAY#}, {YEAR4} at {HOUR24}:{MINUTE}:{SECOND}.")
    print(output)  # Today is Sunday, October 31, 2004, at 13:12:11.
    ```

    ### Returns:
    - A `datetime_ez` object with enhanced functionality.
    """

    def __new__(cls, *args, dt_ :dt.datetime|None=None, **kwargs):
        """
            Create a new instance of the `datetime_ez` class.

            Overrides the standard `__new__` to provide additional functionality for creating an
            instance of `datetime_ez` from an existing `datetime` object using the `dt` parameter.
            If `dt` is provided, its attributes (such as `year`, `month`, etc.) are extracted to
            initialize the new instance. If `dt` isn't provided, the method behaves as a
            standard `datetime` constructor and accepts the usual positional and keyword arguments
            (e.g., `year`, `month`, `day`, etc.).

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
            - `dt` (datetime, optional): An existing `datetime` object. If provided, the new
               `datetime_ez` object will be created using its attributes. Defaults to `None`.
            - `*args`: Positional arguments for creating a standard `datetime` object
              (used if `dt` is not provided).
            - `**kwargs`: Keyword arguments for creating a standard `datetime` object (used
              if `dt` is not provided).

            ### Returns:
            - `datetime_ez`: A new instance of the `datetime_ez` class, either initialized
              from the `dt` object or created using the provided positional and keyword arguments.

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

        if dt_:
            # Create new instance using the provided datetime object
            return super().__new__(
                cls,
                dt_.year,
                dt_.month,
                dt_.day,
                dt_.hour,
                dt_.minute,
                dt_.second,
                dt_.microsecond,
                dt_.tzinfo,  # Keep timezone if present
            )
        # Create new instance using regular datetime constructor
        return super().__new__(cls, *args, **kwargs)

    def ezftime(self, fmt: str) -> str:
        """
        Format a datetime object into a custom string using an enhanced set of macros
        for datetime components.

        ### Key Features:
        - Support for **standard Python datetime format strings** (e.g., `%Y`, `%m`, `%d`).
        - Support for additional **macros** (e.g., `{HOUR12}`, `{MONTH}`).
        - Mix macros and text for highly customized formats while avoiding conflicts.

        ### Example Placeholders and Mappings:
        - `{YEAR4}` → Four-digit year (e.g., `2004`).
        - `{MONTH}` → Full month name (e.g., `October`).
        - `{HOUR24}` → Hour in 24-hour clock notation (e.g., `13`).
        ...

        Returns:
            str: A fully formatted string containing the requested datetime in the given format.

        Examples:
            >>> snap = datetime_ez(2004, 10, 31, 13, 12, 11)

            >>> snap.ezftime("{DAY}, {MONTH} {DAY#}, {YEAR4}, {HOUR12}:{MINUTE}:{SECOND} {AM}")
            "Sunday, October 31, 2004,  01:12:11 PM"

            >>> snap.ezftime("{YEAR4}-{MONTH#}-{DAY#} %H:%M")
            "2004-10-31 13:12"
        """
        return self.strftime(ez_format(fmt))


def make_d8fmt_parser() -> argparse.ArgumentParser:
    """
    Creates and returns an argument parser for the `d8fmt` command-line tool.

    The parser defines a set of command-line arguments for customizing the formatting
    of datetime strings using `ezftime` specifiers. Users can specify format strings,
    toggle verbose or debugging output, and choose between using the canonical reference
    datetime or the current datetime.

    Returns:
        argparse.ArgumentParser: Configured argument parser.

    Arguments:
        - format_string: (optional) The format string containing `ezftime` placeholders.
                         Defaults to `"{DAY3} {MONTH3} {DAY#} {HOUR24}:{MINUTE}:{SECOND}"`.
        - -a / --all: Shows all replacement placeholders and their values in the output.
        - -c / --canonical: Uses the canonical reference datetime for formatting.
        - -o / --print-original: Prints the original input format string before formatting.
        - -t / --print-tokenized: Outputs the intermediate tokenized format string.
        - -v / --verbose: Enables verbose debugging, displaying additional information.
    """
    parser = argparse.ArgumentParser(
        description="Format a string using ezftime format specifiers."
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
        help="Print everything available for debugging purposes.",
    )

    return parser


def run_cli():
    """
    Entry point for the application when accessed via the command line.

    This function provides a command-line interface (CLI) to format strings using the `ezftime`
    format specifiers, which support both standard datetime placeholders and custom macros. Users
    can specify a format string, apply verbose debugging flags, or use predefined options such as a
    canonical date for demonstration.

    ### CLI Arguments:
    - `format_string` (positional, optional): The desired format string with `ezftime` placeholders.
      Defaults to:
      `{DAY3} {MONTH3} {DAY#} {HOUR24}:{MINUTE}:{SECOND}`

      Example: `"{HOUR12}:{MINUTE} {AM}"` → Output: `"01:12 PM"`

    - `-a / --all`: Displays all placeholders and their values in the output format string.
    - `-c / --canonical`: Uses the canonical datetime reference (October 31, 2004 13:12:11.000000).
      If omitted, the current date and time will be used.
    - `-o / --print-original`: Prints the original format string provided by the user.
    - `-t / --print-tokenized`: Prints the tokenized format string, where macros are replaced but no
      datetime placeholders (like `%Y`) have been applied yet.
    - `-v / --verbose`: Enables verbose output, showing all available debug information, including
      the original format string, tokenized string, and final formatted output.

    ### Behavior:
    - If the `--canonical` flag is provided, the canonical datetime (`2004-10-31 13:12:11`) will be
      used for formatting. Otherwise, the current system datetime is used.
    - If `-a / --all` is specified, the format string is automatically replaced with one containing
      all placeholders and their values for demonstration purposes.
    - Errors are handled, with descriptive messages printed to `stderr`:
        - `KeyError`: Missing macro in the format string.
        - Any other unexpected errors result in a generic error message with an exit status `2`.

    ### Returns:
    - None; the program exits with an appropriate exit status:
        - `0` on success.
        - `1` for general errors (e.g., a missing macro).
        - `2` for unexpected errors.

    ### Example Usage:
    #### Basic Usage:
    ```bash
    $ python d8fmt.py "{HOUR12}:{MINUTE} {AM}"
    Output: 01:12 PM
    ```

    #### Show Verbose Output:
    ```bash
    $ python d8fmt.py -v "{DAY}, {MONTH} {DAY#}, {YEAR4} at {HOUR24}:{MINUTE}"
    Original Format String:
    {DAY}, {MONTH} {DAY#}, {YEAR4} at {HOUR24}:{MINUTE}

    Tokenized String (with macros replaced):
    %{A}, %{B} %{d}, %{Y} at %{H}:%{M}

    Formatted String (with datetime values applied):
    Sunday, October 31, 2004 at 13:12
    ```

    #### Use All Placeholders:
    ```bash
    $ python d8fmt.py -a
    Output: day=Sunday Sun 31 mon=October Oct 10 y=04 2004 hr=01PM/13 min=12 s=11.000000 ...
    ```

    #### Use Canonical Datetime:
    ```bash
    $ python d8fmt.py -c "{MONTH} {DAY#}, {YEAR4}, at {HOUR12}:{MINUTE} {AM}"
    Output: October 31, 2004, at 01:12 PM
    ```
    """

    # Build the parer for this app
    parser = make_d8fmt_parser()


    try:
        args = parser.parse_args()
        if args.all:
            args.format_string = "day={DAY} {DAY3} {DAY#} mon={MONTH} {MONTH3} {MONTH#} y={YEAR2}" \
                                 " {YEAR4} hr={HOUR12}{PM}/{HOUR24} min={MINUTE} s={SECOND}." \
                                 "{MICROSEC} DOY={DOY} WeekOfYear={WOY} WeakOfYearIso={WOYISO} " \
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
        print(f"Error: Missing macro in fmt string-{e}. Are macros in format string are defined?",
              file=sys.stderr)
        sys.exit(1)  # Exit code 1 indicates general error

    except Exception as e:
        # Catch other unexpected errors
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)  # Use a different exit code for unexpected failures


if __name__ == "__main__":  # pragma: no cover

    run_cli()
