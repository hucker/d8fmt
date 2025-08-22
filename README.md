# d8fmt - Readable Formatting for Datetimes.

## Quickstart

Install the package:
```bash
pip install d8fmt
```
Format a date using the CLI:
```bash
python -m d8fmt -c "{YEAR4}-{MONTH#}-{DAY#}" 
>> 13:12:00
```
Use it in Python:
```python
from d8fmt import datetime_ez

d = datetime_ez(year=2004, month=10, day=31, hour=13, minute=12, second=0)
print(d.ezftime("{HOUR24}:{MINUTE}:{SECOND} Day of year = {DOY}"))  # Outputs: 13:12:00 Day of year = 305
```


## Format By Example for Datetime
`d8fmt` is a Python module designed to transform canonical datetime examples into deterministic and platform-independent format strings using `strftime` directives. It provides two flexible ways to define readable and human-friendly format strings:
### 1. Canonical Examples
You can specify a **unique, deterministic datetime example** to define how dates should be formatted. The canonical example ensures that all components of the datetime are unique and easily converted into appropriate `strftime` directives.
Example:
``` plaintext
Input: Sunday October 31 2004 13:12:11.000000
Output: "%A %B %d %Y %H:%M:%S.%f"
```
By using this approach, `d8fmt` automatically parses your example and generates the correct format string by detecting unique components like the day, month, year, and time.
### 2. Readable English-Like Macros
For better readability, you can use **tokenized macros** that clearly represent datetime components in plain English. These macros replace cryptic `strftime` directives with easy-to-understand placeholders.
Example:
``` plaintext
Input: {YEAR4}/{MONTH#}/{DAY#} {HOUR24}:{MINUTE}:{SECOND}.{MICROSEC}
Output: "%Y/%m/%d %H:%M:%S.%f"
```
This method is more verbose but ensures clarity and correctness. It’s especially useful for generating consistent and understandable format strings.
### Key Features
- **Deterministic Parsing**: Every component in the canonical example (e.g., October 31, 2004, 13:12:11) is unique, ensuring consistent and accurate parsing into `strftime` formats.
- **Flexibility**: Both human-friendly macros and canonical examples work seamlessly with mixed format strings (e.g., separators like `/`, `-`, or even text).
- **Versatility**: If a part of the input doesn’t match a known macro or directive, it simply passes through as-is.

### Custom Usage Scenarios
1. **Macro-Based Formatting** (English Tokens):
``` python
"{YEAR4}/{MONTH#}/{DAY#}" → "%Y/%m/%d"
```

2. **Canonical-Style Formatting** (Format from a fixed date example):
``` python
"Sunday October 31 2004 13:12:11.000000" → "%A %B %d %Y %H:%M:%S.%f"
```

3. **Mixed Styles (not really recommended)**:
``` python
"Oct {DAY#}, {YEAR4} at {HOUR12}:{MINUTE} {PM}" → "%b %d, %Y at %I:%M %p"
```

### Notes
- Canonical examples and macros are **mutually compatible** and can be mixed freely in a single format.
- Common separators like spaces, slashes (`/`), or dashes (`-`) pass through unchanged.
- Avoid using overly long text as part of your format, as it may unexpectedly coincide with valid components.


| **Canonical<br>Oct 31 2004 13:12:11** | **Macro**    | **Description**                                 | **%Format** |
|---------------------------------------|--------------|-------------------------------------------------|--------|
| `01`                                  | `{HOUR12}`   | Hour in 12-hour clock (zero-padded)           | `%I`   |
| `13`                                  | `{HOUR24}`   | Hour in 24-hour clock (zero-padded)           | `%H`   |
| `305`                                 | `{DOY}`      | Day of the year (1–366, zero-padded)          | `%j`   |
| `04`                                  | `{YEAR2}`    | Year without century (last two digits)        | `%y`   |
| `2004`                                | `{YEAR4}`    | Year with century                             | `%Y`   |
| `October`                             | `{MONTH}`    | Full month name                               | `%B`   |
| `Oct`                                 | `{MONTH3}`   | Abbreviated month name                        | `%b`   |
| `10`                                  | `{MONTH#}`   | Month as a number (zero-padded, 01–12)        | `%m`   |
| `Sunday`                              | `{DAY}`      | Full weekday name                             | `%A`   |
| `Sun`                                 | `{DAY3}`     | Abbreviated weekday name                      | `%a`   |
| `31`                                  | `{DAY#}`     | Day of the month (zero-padded)                | `%d`   |
| `12`                                  | `{MINUTE}`   | Minute (zero-padded)                          | `%M`   |
| `11`                                  | `{SECOND}`   | Second (zero-padded)                          | `%S`   |
| `.000000`                             | `{MICROSEC}` | Microsecond (zero-padded, 6 digits)           | `%f`   |
| `AM`                                  | `{AM}`       | AM/PM marker                                  | `%p`   |
| `PM`                                  | `{PM}`       | AM/PM marker                                  | `%p`   |
| `44`                                  | `{WOY}`      | Week of the year (Sunday as first day)        | `%U`   |
| `43`                                  | `{WOYISO}`   | ISO week number of the year (Mon as first day)| `%W`   |
| `7`                                   | `{WDAY#ISO}` | Day of the week (ISO, Monday=1 to Sunday=7)   | `%u`   |
| `0`                                   | `{WDAY#}`    | Day of the week (Sunday-based, 0=Sun to 6=Sat)| `%w`   |
| _N/A_                                 | `{TZ}`       | Timezone abbreviation                         | `%Z`   |
| _N/A_                                 | `{UTCOFF}`   | UTC offset in the form ±HHMM                  | `%z`   |

Here are some examples of converting these format strings into datetime ready format strings.

```shell
>>> d8fmt.snap_fmt("2004-10-31")
'%Y-%m-%d'
>>> d8fmt.snap_fmt("2004-10-31 13-12-11")
'%Y-%m-%d %H-%M-%S'
>>>d8fmt.snap_fmt("Oct. 31 2004 01-12-11 PM")
'%b. %d %Y %I-%M-%S %p'
>>d8fmt.snap_fmt("{YEAR4}-{MONTH#}-{DAY#}T{HOUR24}:{MINUTE}:{SECOND}")
'%Y-%m-%dT%H:%M:%S'
>>d8fmt.snap_fmt("{YEAR4}-{MONTH#}-{DAY#}T{HOUR24}:{MINUTE}:{SECOND}.{MICROSEC}")
'%Y-%m-%dT%H:%M:%S.%f'
```

Note: `d8fmt` does NOT yet support timezones or offsets.

---

## Features

- **Token Conversion**: Converts canonical components (e.g., `2004`, `31`, `October`) into matching `strftime` directives (e.g., `%Y`, `%d`, `%B`).
- **Time Zone Validation**:
  - Prohibits timezone abbreviations (e.g., `PST`, `GMT`).
  - Enforces offsets like `+/-dddd` to have a leading space.
- **Fractional Seconds Support**: Encodes fractional seconds via `%<N>f`, where `N` determines the number of zeros in the example.
- **Error Handling**: Raises a `ValueError` for unsupported formats or invalid tokens.
- **Round-Trip Validation**: Ensures that transformed formats can accurately round-trip the `canonical` example.


---

## Installation

Clone the repository and ensure you have Python 3.x installed along with required libraries like `pytest` for testing.

```bash
git clone <https://github.com/hucker/d8fmt>
cd d8fmt
```

---

## Usage

### Import the Module

```python
from d8fmt import ez_format, is_zone_free, datetime_ez
```

### Override datetime object

The class `datetime_ez` is provided allowing you to just drop in the new class like this.

```shell
>>d = d8fmt.datetime_ez(year=2025,month=8,day=15,hour=13,minute=12,second=11)

>>d.ezftime("{DAY}-{DAY#}-{MONTH}-{YEAR2}")
'Friday-15-August-25'
>>d.ezftime("{DAY}-{MONTH}-{YEAR2} {HOUR12}:{MINUTE}:{SECOND} {PM}")
'Friday-August-15 01:12:11 PM'
>>d.ezftime("{DAY3}-{MONTH3}-{YEAR2} {HOUR24}:{MINUTE}:{SECOND} {PM}")
'Fri-Aug-25 13:12:11 PM'
>>d.ezftime("Sunday Oct 31 2004  13:12:11.000000")
'Friday Aug 15 2025  13:12:11.000000'
````
It is possible that it is not convenient to just use datetime_ez objects everwhere. 
The easy way to make this happen is to create a datetime_ez from a datetime object like this

```shell
import datetime
>> from d8fmt import datetime_ez
>> dt_now = datetime.datetime.now()
datetime.datetime(2025, 8, 21, 1, 18, 24, 157679)
>> dt_ez = datetime_ez(dt=dt_now)    #<- create a copy from an existing datetime object?
datetime.datetime(2025, 8, 21, 1, 18, 24, 157679)
>> print(dt_ez.ezftime('{Year} {Month} {Day}'))
2025 08 21
```

### Transform a Format String
You shouldn't really  need the format string directly, but it is readily accessible by using the snap_fmt function
to convert an ez format string into a `datetime` aware format string.  Internally, all the `ezftime` method does is
run the `snap_fmt` function on the format string that you provide which is then passed to the `datetime`'s 
`strftime` method.


```shell
from d8fmt import snap_fmt

output_format = snap_fmt("2004-10-31")  # Example input
print(output_format)  # Output: '%Y-%m-%d'
```

### Validate Time Zones
Check if a format string is free from unsupported time zone abbreviations or patterns:
```python
from d8fmt import is_zone_free

is_zone_free("2004-10-31T13:12:11 +0530")  # Raises ValueError
```

---

## CLI

A command line interface is available for test purposes.  It is very similar to the date command on
Mac/PC/Linux, but it also gives you a way to interactively test yur format strings.

```shell

(d8fmt) chuck@Chucks-Mac-mini src % python -m d8fmt --help
Format a string using ezftime format specifiers and return appropriate exit codes.

positional arguments:
  format_string         The format string to use, with ezftime placeholders (e.g., '{HOUR12}:{MINUTE} {AM}'). If not provided, a default format will be used.

options:
  -h, --help            show this help message and exit
  -a, --all             Use a format string that shows all replacements
  -c, --canonical       Use the canonical datetime reference (October 31, 2004 13:12:11.000000) for formatting. If not provided, the current datetime is used.
  -o, --print-original  Print the original format string provided as input.
  -t, --print-tokenized
                        Print the tokenized string after macro substitutions.
  -v, --verbose         Print everithing available for debugging purposes.


(d8fmt) chuck@Chucks-Mac-mini src % python -m d8fmt       
Thu Aug 21 11:38:02

(d8fmt) chuck@Chucks-Mac-mini src % python -m d8fmt -c
Sun Oct 31 13:12:11

(d8fmt) chuck@Chucks-Mac-mini src % python -m d8fmt -a
day=Thursday Thu 21 mon=August Aug 08 y=25 2025 hr=11AM/11 min=38 s=17.912408 DOY=233 WeekOfYear=33 WeakOfYearIso=33 WDAY#=4 WDAY#ISO=4 LOCALE=08/21/25


(d8fmt) chuck@Chucks-Mac-mini src % python -m d8fmt -v
Original Format String:
{DAY3} {MONTH3} {DAY#} {HOUR24}:{MINUTE}:{SECOND}

Tokenized String (with macros replaced):
%a %b %d %H:%M:%S

Formatted String (with datetime values applied):
Thu Aug 21 11:38:38


(d8fmt) chuck@Chucks-Mac-mini src % python -m d8fmt "{MONTH#}/{DAY#}/{YEAR4} {HOUR24}:{MINUTE}:{SECOND}"
08/21/2025 11:43:53


````

## Testing

Run tests to confirm functionality and validation.  As it currently sits `d8fmt` has 100% code coverage,
using 107 tests with a lint scroe of 9.78/10.

```bash
pytest test_d8fmt.py
```

Example Output:
```plaintext
========================== test session starts =========================
collected 107 items

test_d8fmt.py ........................                                    [100%]

=========================== 107 passed in 0.11s =========================
```

---


## Contribution

Feel free to submit issues or propose enhancements via pull requests. Be sure to follow the existing code structure and guidelines.

---

## License

[MIT License](LICENSE)

---

## Acknowledgments

This module adheres to strict rules for datetime handling with influences from ISO 8601 standards.
