# oj-toolkit

[![License](https://img.shields.io/github/license/ownjoo/ownjoo-toolkit)](LICENSE)
[![Top language](https://img.shields.io/github/languages/top/ownjoo/ownjoo-toolkit)](https://github.com/ownjoo/ownjoo-toolkit) [![Stars](https://img.shields.io/github/stars/ownjoo/ownjoo-toolkit)](https://github.com/ownjoo/ownjoo-toolkit/stargazers) [![Forks](https://img.shields.io/github/forks/ownjoo/ownjoo-toolkit)](https://github.com/ownjoo/ownjoo-toolkit/forks) [![Issues](https://img.shields.io/github/issues/ownjoo/ownjoo-toolkit)](https://github.com/ownjoo/ownjoo-toolkit/issues) [![Pull requests](https://img.shields.io/github/issues-pr/ownjoo/ownjoo-toolkit)](https://github.com/ownjoo/ownjoo-toolkit/pulls)

Centralized shared utilities library for all ownjoo projects. Provides battle-tested functions for type validation, data parsing, and progress logging.

## Overview

This library is the single source of truth for shared utilities across ownjoo projects. All projects should import common utilities from here rather than implementing their own versions.

### Modules

- **`parsing`** — Type validation, datetime conversion, nested data extraction, and attribute/method resolution on arbitrary Python objects
- **`logging`** — Standardized logging configuration and progress tracking decorators
- **`console`** — Terminal and console output utilities (stdout, stderr, formatting)
- **`data`** — Flexible data handling mixins
- **`asynchronous`** — Async utilities (chunking, generators, coroutine timeouts)
- **`timing`** — Wall-clock timeout decorator for blocking (synchronous) calls
- **`ops`** — Composable, nestable op classes for data-processing/logic chains, with a registry + `compile()` for building the same chains from a declarative spec dict

## Installation

Install from PyPI:

```bash
pip install oj-toolkit
```

Or install from the repository:

```bash
pip install git+https://github.com/ownjoo/ownjoo-toolkit.git
```

For local development:

```bash
git clone https://github.com/ownjoo/ownjoo-toolkit.git
cd ownjoo-toolkit
pip install -e ".[dev]"
```

## Quick Start

### Stream Output

```python
from oj_toolkit import Output

# Create an output handler
output = Output()

# Write to stdout
output.out("Hello", "World")  # Hello World

# Write to stderr
output.err("Error:", "Something went wrong")  # Error: Something went wrong

# Custom separators and line endings
output.out("a", "b", "c", sep="|", end=" - done\n")  # a|b|c - done

# Redirect to custom streams (useful for testing or file output)
import io
file_stream = io.StringIO()
output = Output(stdout=file_stream)
output.out("This goes to the StringIO")
print(file_stream.getvalue())  # This goes to the StringIO\n
```

### Colored Output

```python
from oj_toolkit import Output, Color

output = Output()

# Shorthand methods for common colors
output.out_red("Error message")      # Red text to stdout
output.out_green("Success!")         # Green text to stdout
output.out_yellow("Warning")         # Yellow text to stdout
output.out_blue("Information")       # Blue text to stdout

# Shorthand methods for stderr
output.err_red("Critical error")     # Red text to stderr
output.err_yellow("Minor warning")   # Yellow text to stderr

# Custom color combinations
output.out_colored("Bold Red", color=Color.BOLD + Color.RED)
output.out_colored("Cyan background", color=Color.BG_CYAN)

# Use Color constants directly
from oj_toolkit.console import Color
colored_text = Color.colorize("Important", Color.BOLD + Color.RED)
print(colored_text)
```

### Chainable Colored Text

```python
from oj_toolkit import Output

output = Output()

# Build multi-color lines with a fluent API
output.segment().red("ERROR: ").white("something went wrong").cyan(" (code: 500)").out()

# Chain to stderr
output.segment().bold("Status: ").green("OK").reset(" (2.5s)").err()

# Build a ColoredText independently
from oj_toolkit import ColoredText

text = (ColoredText()
    .bold("Build: ")
    .green("passed")
    .reset(" | ")
    .yellow("warnings: 3")
)
print(text)  # Rendered with ANSI codes
```

### Parsing & Validation

```python
from oj_toolkit import validate, get_datetime, str_to_list, dig, dig_many, Digger

# Validate and convert types
result = validate('123', exp=int, converter=int)  # Returns: 123
result = validate('invalid', exp=int, default=0)  # Returns: 0 (validation failed)

# Convert string to list
items = str_to_list('a,b,c')  # Returns: ['a', 'b', 'c']
items = str_to_list('a;b;c', separator=';')  # Returns: ['a', 'b', 'c']

# Parse datetime from multiple formats
dt = get_datetime('2024-01-15T10:30:00')  # ISO 8601
dt = get_datetime(1705318200)  # Unix timestamp
dt = get_datetime('Mon, 15 Jan 2024 10:30:00 GMT')  # HTTP date

# Extract and validate nested values using a jmespath expression
data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
name = dig(data, path='users[0].name', exp=str)  # Returns: 'Alice'
names = dig(data, path='users[*].name', exp=list)  # Returns: ['Alice', 'Bob']

# Fallback chain: first matching path wins (handy for optional/renamed fields)
name = dig(data, path=['users[0].nickname', 'users[0].name'], exp=str)  # Returns: 'Alice'

# Extract several fields in one call
fields = dig_many(
    data,
    paths={'first_name': 'users[0].name', 'second_name': 'users[1].name'},
    post_processor=None,  # skip validate() and return raw matches
)
# Returns: {'first_name': 'Alice', 'second_name': 'Bob'}

# Bind a path once, reuse it against many objects
get_name = Digger(path='name', exp=str, default='')
[get_name(user) for user in data['users']]  # Returns: ['Alice', 'Bob']

# Constrain a string result with a regex (checked via re.fullmatch after conversion)
mac = dig({'device': {'mac': 'AA:BB:CC:DD:EE:FF'}}, path='device.mac', exp=str,
          pattern=r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}')
# Returns: 'AA:BB:CC:DD:EE:FF'
```

> **Note:** if the path resolves to nothing (missing key/index, or `src` doesn't contain it),
> `dig()`'s default `post_processor` (`validate()`) still runs and returns `default` (`None`
> unless set) -- a missing path never silently drops `default` in favor of a bare `None`.
> Passing no `exp=` means "accept any type, no isinstance check" -- not "always fail". Pass
> `exp=<type>` to add a type check, or `post_processor=None` to bypass validation entirely and
> get the raw match untouched.

### Logging Setup

Call `configure_logging` once at application startup (Lambda handler, CLI `main()`, FastAPI lifespan). Libraries should never call it — they only use `logging.getLogger(__name__)`.

```python
from oj_toolkit.logging import configure_logging

# Local development — human-readable output, WARNING+
configure_logging(service='my-service')

# Deployed environments — JSON lines to stdout, WARNING+
configure_logging(service='my-service', env='prod')

# Explicit level (int constant or string)
configure_logging(service='my-service', level=logging.INFO)
configure_logging(service='my-service', level='DEBUG')

# Or set LOG_LEVEL env var — configure_logging will read it
# LOG_LEVEL=INFO configure_logging(service='my-service')
```

**Local output** (`env='local'`): human-readable, with level names colorized when stdout is a TTY (`NO_COLOR` and `TERM=dumb` are respected):
```
2026/04/13 12:00:00 - my_module - INFO - started processing
```

**Deployed output** (`env='prod'` or any non-local value):
```json
{"timestamp": "2026-04-13T12:00:00+00:00", "level": "INFO", "logger": "my_module", "service": "my-service", "env": "prod", "message": "started processing"}
```

`configure_logging` is idempotent — safe to call multiple times, only the first call takes effect. Noisy third-party loggers (`urllib3`, `boto3`, `botocore`, `s3transfer`, `requests`) are silenced to WARNING automatically.

**Extending for AWS Lambda** — subclass `JsonFormatter` and override `extra_fields` to inject per-request context:

```python
from oj_toolkit.logging.formatters import JsonFormatter

class LambdaFormatter(JsonFormatter):
    def __init__(self, service, env, context):
        super().__init__(service, env)
        self.context = context

    def extra_fields(self, record):
        return {'aws_request_id': self.context.aws_request_id}
```

### Progress Logging

```python
from oj_toolkit import timed_generator, timed_async_generator
import logging

# configure_logging should be called at app startup before using these decorators
configure_logging(service='my-service', level=logging.INFO)

@timed_generator(log_progress_label="records", log_progress_interval=1000)
def fetch_records():
    for i in range(50000):
        yield {'id': i, 'data': f'record_{i}'}

for record in fetch_records():
    process(record)

# Output:
# 2026/04/13 10:30:00 - oj_toolkit.logging.decorators - INFO - Started records at 2026-04-13T10:30:00+00:00
# 2026/04/13 10:31:00 - oj_toolkit.logging.decorators - INFO - Fetched 1000 records so far
# ... (every 1000 items)
# 2026/04/13 10:35:00 - oj_toolkit.logging.decorators - INFO - Ended records at 2026-04-13T10:35:00+00:00
# 2026/04/13 10:35:00 - oj_toolkit.logging.decorators - INFO - Yielded 50000 records in 0:05:00
```

For async generators:

```python
@timed_async_generator(log_progress_label="items", log_progress_interval=500)
async def fetch_items_async():
    for i in range(10000):
        yield {'id': i}

async for item in fetch_items_async():
    await process(item)
```

### Timeouts

```python
from oj_toolkit import timeout, async_timeout

# Blocking call -- runs on a daemon thread, waits up to `seconds`
@timeout(seconds=5)
def slow_call():
    ...

try:
    slow_call()
except TimeoutError as e:
    print(f'gave up waiting: {e}')

# Coroutine -- built on asyncio.wait_for, actually cancels the inner call
@async_timeout(seconds=5)
async def slow_async_call():
    ...

try:
    await slow_async_call()
except TimeoutError as e:
    print(f'gave up waiting: {e}')
```

> **Sync vs. async:** `timeout()` can't forcibly kill a thread -- past the deadline it
> raises and returns control to the caller, but the abandoned call keeps running in the
> background on a daemon thread (so it never blocks interpreter exit, but it also never
> stops). `async_timeout()` is stronger: `asyncio.wait_for` actually cancels the inner
> coroutine at its next `await` point. Prefer `async_timeout` for coroutines; reach for
> `timeout` only for blocking/sync calls.

## API Reference

### `console` Module

#### `Output(stdout=None, stderr=None)`

Simple wrapper for writing to stdout and stderr streams.

- **Parameters:**
  - `stdout` (TextIO): The output stream for normal output. Default: sys.stdout
  - `stderr` (TextIO): The output stream for error messages. Default: sys.stderr

- **Methods:**

##### `out(*args, sep=' ', end='\n', flush=False)`

Write to standard output stream.

- **Parameters:**
  - `*args`: Values to write (converted to strings)
  - `sep` (str): Separator between args. Default: space
  - `end` (str): String appended after the last value. Default: newline
  - `flush` (bool): Force flush the stream. Default: False

**Example:**

```python
output = Output()
output.out("Hello", "World")  # Hello World
output.out("Status:", "OK", end=" - done\n")  # Status: OK - done
output.out("a", "b", "c", sep="|")  # a|b|c
```

##### `err(*args, sep=' ', end='\n', flush=False)`

Write to standard error stream.

- **Parameters:**
  - `*args`: Values to write (converted to strings)
  - `sep` (str): Separator between args. Default: space
  - `end` (str): String appended after the last value. Default: newline
  - `flush` (bool): Force flush the stream. Default: False

**Example:**

```python
output = Output()
output.err("Error:", "File not found")  # Error: File not found
output.err("code=404", "msg=Not Found", sep="|", flush=True)  # code=404|msg=Not Found
```

**Stream Redirection:**

```python
import io

# Capture output for testing
stdout_capture = io.StringIO()
stderr_capture = io.StringIO()
output = Output(stdout=stdout_capture, stderr=stderr_capture)

output.out("to stdout")
output.err("to stderr")

print(stdout_capture.getvalue())  # to stdout\n
print(stderr_capture.getvalue())  # to stderr\n
```

##### `out_colored(*args, color='', sep=' ', end='\n', flush=False)`

Write colored text to stdout using ANSI escape codes.

- **Parameters:**
  - `*args`: Values to write (converted to strings)
  - `color` (str): ANSI color code (e.g., `Color.RED`, `Color.BOLD + Color.GREEN`)
  - `sep` (str): Separator between args. Default: space
  - `end` (str): String appended after the last value. Default: newline
  - `flush` (bool): Force flush the stream. Default: False

**Example:**

```python
from oj_toolkit import Output, Color

output = Output()
output.out_colored("Error", color=Color.RED)
output.out_colored("Bold Green", color=Color.BOLD + Color.GREEN)
output.out_colored("Status", "OK", color=Color.BLUE)
```

##### `err_colored(*args, color='', sep=' ', end='\n', flush=False)`

Write colored text to stderr using ANSI escape codes. Same parameters as `out_colored()`.

**Example:**

```python
output.err_colored("Critical error", color=Color.BOLD + Color.RED)
```

##### Shorthand Color Methods

Convenient methods for common colors:

- `out_red(*args, ...)` — Red text to stdout
- `out_green(*args, ...)` — Green text to stdout
- `out_yellow(*args, ...)` — Yellow text to stdout
- `out_blue(*args, ...)` — Blue text to stdout
- `err_red(*args, ...)` — Red text to stderr
- `err_green(*args, ...)` — Green text to stderr
- `err_yellow(*args, ...)` — Yellow text to stderr

**Example:**

```python
output = Output()
output.out_green("Success!")
output.out_red("Error occurred")
output.err_yellow("Warning: deprecated")
```

##### `segment() → ColoredText`

Create a chainable `ColoredText` builder bound to this output's streams.

**Example:**

```python
output = Output()
output.segment().red("ERROR: ").white("critical failure").out()
output.segment().yellow("WARNING").cyan(" - deprecated").err()

# Complex multi-color line
(output.segment()
    .bold("Status: ")
    .green("OK")
    .reset(" (")
    .cyan("2.5s")
    .reset(")")
    .out())
```

#### `Color` - ANSI Color Constants and Utilities

Static class providing ANSI color codes for terminal output.

**Attributes:**

- **Reset:** `Color.RESET` — Reset to default terminal color
- **Styles:** `Color.BOLD`, `Color.DIM`
- **Foreground colors:** `Color.RED`, `Color.GREEN`, `Color.YELLOW`, `Color.BLUE`, `Color.MAGENTA`, `Color.CYAN`, `Color.WHITE`
- **Background colors:** `Color.BG_RED`, `Color.BG_GREEN`, `Color.BG_YELLOW`, `Color.BG_BLUE`, `Color.BG_MAGENTA`, `Color.BG_CYAN`, `Color.BG_WHITE`

**Static Methods:**

##### `Color.colorize(text, color='', reset=True)`

Apply ANSI color codes to text.

- **Parameters:**
  - `text` (str): The text to colorize
  - `color` (str): Color code to apply (can be combined with `+`, e.g., `Color.BOLD + Color.RED`)
  - `reset` (bool): Append `Color.RESET` at the end. Default: True

- **Returns:** The text wrapped in color codes

**Example:**

```python
from oj_toolkit import Color

# Single color
colored = Color.colorize("Error", Color.RED)

# Combined colors
important = Color.colorize("CRITICAL", Color.BOLD + Color.RED)

# No reset (continue coloring next output)
colored = Color.colorize("text", Color.GREEN, reset=False)
```

**Available Color Combinations:**

```python
Color.BOLD + Color.RED          # Bold red text
Color.DIM + Color.YELLOW        # Dim yellow text
Color.BOLD + Color.BG_BLUE      # Bold text on blue background
```

#### `ColoredText` - Chainable Colored Text Builder

Accumulates text segments with associated colors and renders them as a single ANSI-coded string.

**Constructor:** `ColoredText(stdout=None, stderr=None)`

**Chaining methods** — each returns `self` for fluent chaining:

- `add(text, color='')` — Add a segment with an explicit color code
- `red(text)`, `green(text)`, `yellow(text)`, `blue(text)` — Shorthand color methods
- `magenta(text)`, `cyan(text)`, `white(text)` — Additional color shorthands
- `bold(text)`, `dim(text)` — Style shorthands
- `reset(text)` — Add text with `Color.RESET` applied
- `from_iter(iterable)` — Consume an iterable of `(text, color)` tuples

**Output methods:**

- `out(sep='', end='\n', flush=False)` — Print to stdout
- `err(sep='', end='\n', flush=False)` — Print to stderr
- `str(text)` — Render as ANSI-coded string
- `iter(text)` — Iterate over `(text, color)` segment tuples

**Example:**

```python
from oj_toolkit import ColoredText, Color

# Fluent chaining
text = (ColoredText()
    .red("ERROR: ")
    .white("something went wrong")
    .cyan(" (code: 500)")
)
print(text)  # Renders with ANSI codes

# Consume a generator of (text, color) tuples
def color_gen():
    yield ("Status: ", Color.BOLD)
    yield ("OK", Color.GREEN)

text = ColoredText().from_iter(color_gen())
text.out()

# Iterate over segments
for segment_text, color in text:
    print(f"{color}{segment_text}\033[0m", end="")
```

### Formatting Utilities

#### `Table` - Smart Table Builder

Build ASCII/Unicode tables with automatic input detection and formatting.

```python
from oj_toolkit import Table, tabulated

# Create a table with dict input (auto-detects headers)
data = [
    {"name": "Alice", "status": "OK"},
    {"name": "Bob", "status": "ERROR"},
]
table = Table()
table.add_rows(data)
print(table)

# Create a table with explicit headers
table = Table(headers=["Name", "Status", "Duration"], columns=3)
table.add_row("Task 1", "OK", "2.5s")
table.add_row("Task 2", "ERROR", "1.2s")
print(table)

# Use as a decorator
@tabulated(headers=["ID", "Value"])
def get_results():
    yield (1, "First")
    yield (2, "Second")
    yield (3, "Third")

get_results()  # Prints results in formatted table

# Customize table appearance
table = Table(headers=["A", "B"], style="rounded", padding=2)
table.add_row("1", "2")
print(table)  # Uses rounded Unicode borders
```

**Styles:** `'auto'` (auto-detect Unicode support), `'ascii'`, `'rounded'`, `'double'`, `'single'`, `'none'`

**Smart Input Detection:**
- Dict input → extracts headers from keys
- List of tuples (2 elements) → treats as key-value pairs
- List of tuples (3+ elements) → treats as rows
- List of strings → treats each as a row

#### `Box` - Text Box Builder

Wrap text in decorative boxes with multiple border styles.

```python
from oj_toolkit import Box, in_box

# Create a simple box
box = Box(style="rounded", padding=1)
box.add_line("Hello from a box")
box.add_line("Multiple lines supported")
print(box)

# Box with title
box = Box(style="double", title="Status", width=30)
box.add_line("Operation complete")
print(box)

# Use as a decorator
@in_box(style="rounded", title="Result")
def show_result():
    return "Success!"

show_result()  # Prints result in a box

# Add multiple lines at once
box = Box(style="ascii")
box.add_lines(["Line 1", "Line 2", "Line 3"])
print(box)
```

**Styles:** `'auto'`, `'ascii'`, `'rounded'`, `'double'`, `'single'`, `'solid'`, `'none'`

#### `status_line` - Format Label-Value Pairs

Format simple status lines with optional colors.

```python
from oj_toolkit import status_line, Color

# Basic status line
output = status_line("Status", "OK")  # Status: OK

# With color
output = status_line("Status", "OK", color=Color.GREEN)

# Custom separator
output = status_line("Name", "Alice", sep=" = ")  # Name = Alice
```

#### `progress_bar` - Text-Based Progress Bar

Display a text-based progress bar with percentage.

```python
from oj_toolkit import progress_bar

# Default bar
bar = progress_bar(75)  # ██████████████░░░░░░   75%

# Custom width and characters
bar = progress_bar(50, width=10, filled="=", empty="-")  # =====-----  50%

# With label
bar = progress_bar(30, width=20, label="Loading")  # Loading: ██████░░░░░░░░░░░░   30%

# All variations
progress_bar(0)      # Empty bar
progress_bar(50)     # Half-filled bar
progress_bar(100)    # Full bar (all filled)
```

#### `status_badge` - Semantic Status Indicators

Display colored status badges with semantic meaning.

```python
from oj_toolkit import status_badge

# Semantic status badges
badge = status_badge("READY", "ok")        # [OK] READY (green)
badge = status_badge("FAILED", "error")    # [ERROR] FAILED (red)
badge = status_badge("PARTIAL", "warning") # [WARNING] PARTIAL (yellow)
badge = status_badge("INFO", "info")       # [INFO] INFO (cyan)
```

**Status types:** `'ok'` (green), `'error'` (red), `'warning'` (yellow), `'info'` (cyan, default)

#### Decorator: `@status_wrapped` - Wrap Function Output with Status

Automatically prepend a status badge to function output.

```python
from oj_toolkit import status_wrapped

@status_wrapped(status="ok")
def operation():
    return "Operation complete"

operation()  # Prints: [OK] Operation complete (in green)

@status_wrapped(status="error")
def failed_operation():
    return "Something went wrong"

failed_operation()  # Prints: [ERROR] Something went wrong (in red)
```

**Example: Combining Formatters**

```python
from oj_toolkit import Table, Box, status_line, Color

# Use formatters together for complex layouts
results = Table(headers=["Task", "Status"])
results.add_row("Build", "OK")
results.add_row("Tests", "OK")
results.add_row("Deploy", "FAILED")

box = Box(style="double", title="Build Summary")
box.add_line(str(results))
print(box)

# Status indicator with color
print(status_line("Overall", "FAILED", color=Color.RED))
```

#### Terminal Detection

##### `detect_color_support() → bool`

Returns `True` if ANSI color output is appropriate for the current environment.

Checks in order: stdout is a real TTY → `NO_COLOR` env var → `TERM=dumb` → `COLORTERM=truecolor|24bit`.

Used internally by `configure_logging` to choose between `ColoredHumanFormatter` and `HumanFormatter`.

```python
from oj_toolkit.console import detect_color_support

if detect_color_support():
    print(Color.GREEN + "ready" + Color.RESET)
else:
    print("ready")
```

##### `detect_unicode_support() → bool`

Returns `True` if the terminal likely supports Unicode characters. Used internally to choose between ASCII and Unicode box/table borders.

Checks `NO_COLOR`/`CI`/`TERM` env vars first, then verifies `sys.stdout.encoding` can actually
encode a box-drawing character -- this catches Windows consoles that default to a codepage
(`cp1252`, `cp437`, etc.) that can't, even though the platform/terminal is otherwise
Unicode-capable. Set `PYTHONIOENCODING=utf-8` (or use Windows Terminal with a UTF-8 codepage)
to get Unicode borders on Windows instead of the ASCII fallback.

### `parsing` Module

#### `validate(v, exp=None, default=None, converter=None, validator=None, pattern=None, **kwargs)`

Generic validation utility that converts and validates a value.

- **Parameters:**
  - `v` (Any): The value to validate
  - `exp` (Type): Expected type. Enables automatic converter selection (list → str_to_list, datetime → get_datetime). If `None`, no isinstance check is performed -- any type passes (see `validator` below)
  - `default` (Any): Return this if validation fails, or `v` is missing/`None`. Default: None
  - `converter` (Callable): Custom converter function. Default: auto-selected based on exp. Auto-selection is limited to `list`/`datetime` -- `bool`/`int`/`float`/etc. are pass-through unless you supply your own `converter=`
  - `validator` (Callable): Custom validator function(result, exp, **kwargs) → bool. Default: isinstance check (`exp=None` always passes; a non-type `exp` is rejected rather than raising)
  - `pattern` (str | re.Pattern): Optional regex checked via `re.fullmatch` against the result, but only when the result is a `str` -- ignored for other types. Applied after conversion/validation succeed; a mismatch falls back to `default`
  - `**kwargs`: Passed to converter and validator

- **Returns:** Converted and validated value, or default if validation fails

**Example:**

```python
# Auto-detect converter based on type
numbers = validate('1,2,3', exp=list)  # Returns: ['1', '2', '3']
dt = validate('2024-01-15T10:30:00', exp=datetime)  # Returns: datetime object

# exp=bool/int/float do NOT auto-coerce strings -- pass converter= explicitly for that
validate('42', exp=int)                    # Returns: None ('42' is a str, not an int)
validate('42', exp=int, converter=int)     # Returns: 42

# Regex-constrain a string result
validate('AA:BB:CC:DD:EE:FF', exp=str, pattern=r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}')
# Returns: 'AA:BB:CC:DD:EE:FF'
validate('not-a-mac', exp=str, pattern=r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}', default='invalid')
# Returns: 'invalid'

# Custom converter and validator
def to_upper(v, *args, **kwargs):
    return str(v).upper()

def is_uppercase(v, *args, **kwargs):
    return v.isupper()

result = validate('hello', converter=to_upper, validator=is_uppercase)
# Returns: 'HELLO'
```

#### `str_to_list(v, separator=',', **kwargs)`

Convert a string to a list by splitting on a separator.

- **Parameters:**
  - `v` (str): The string to split. Non-strings return unchanged
  - `separator` (str): Delimiter to split on. Empty string returns value unchanged
  - `**kwargs`: Additional arguments (unused, for compatibility)

- **Returns:** List of strings, or original value if not a string

**Example:**

```python
str_to_list('a,b,c')  # ['a', 'b', 'c']
str_to_list('a;b;c', separator=';')  # ['a', 'b', 'c']
str_to_list(None)  # None
```

#### `get_datetime(v, format_str=None, **kwargs)`

Parse a value into a datetime object from multiple input formats.

Supports:
- Numeric timestamps (seconds since epoch)
- ISO 8601 strings (YYYY-MM-DDTHH:MM:SS)
- HTTP date format (Sun, 06 Nov 1994 08:49:37 GMT)
- Custom format via `format_str` parameter

- **Parameters:**
  - `v` (datetime | float | str | None): Value to parse
  - `format_str` (str): Custom strptime format string
  - `**kwargs`: Additional arguments (unused)

- **Returns:** datetime object, or None if parsing fails

**Example:**

```python
get_datetime('2024-01-15T10:30:00')  # ISO 8601
get_datetime(1705318200)  # Unix timestamp
get_datetime('Mon, 15 Jan 2024 10:30:00 GMT')  # HTTP date
get_datetime('01/15/2024 10:30:00', format_str='%m/%d/%Y %H:%M:%S')  # Custom
```

#### `dig(src, path=None, pop=False, post_processor=validate, **kwargs)`

Extract and post-process a value from a nested data structure, using [jmespath](https://jmespath.org/)
under the hood (`jmespath` is a required dependency).

> **Compilation caching:** compiled jmespath expressions are cached in a process-global
> `lru_cache(maxsize=256)`, keyed by the expression string. A bare `dig()` call already avoids
> recompiling a repeated path -- this isn't a `Digger`-only optimization. The cache holds up to
> 256 distinct expressions across the whole process (shared by every `dig()`/`Digger` caller),
> LRU-evicted beyond that.

- **Parameters:**
  - `src` (Mapping | Sequence): Data structure to navigate
  - `path` (int | str | list | None):
    - `str` — a jmespath expression, e.g. `'users[0].name'`, `'users[*].name'`, `'users[?id==\`2\`].name'`
    - `int` — shorthand for a single top-level index, e.g. `1` is equivalent to `'[1]'`
    - `list[int | str]` — a fallback chain: each candidate is tried in order and the first
      one whose result isn't `None` wins (handy for optional/renamed fields)
    - `None` — treat `src` itself as the value to post-process
  - `pop` (bool): If `True`, delete the terminal key/index of the *winning* expression from
    its container after extracting the value (mutates `src` in place). Only honored when that
    expression's terminal segment is unambiguous (no wildcards, filters, or projections) --
    otherwise it's refused with a logged warning and the value is still returned unpopped.
  - `post_processor` (Callable): Function to post-process the found value. Default: `validate()`.
    Pass `None` to skip post-processing and get the raw match.
  - `**kwargs`: Passed to `post_processor`

- **Returns:** Post-processed value. If extraction fails or no candidate path matches, the
  post-processor (default `validate()`) still runs and returns `default` (`None` unless set) --
  unless `post_processor=None`, in which case the raw (possibly missing/`None`) value is returned
  untouched with no default substitution.

> **Type checkers:** pass `exp=<type>` to get a precise `<type> | None` return type instead of `Any`
> (`dig(data, path='...', exp=str)` type-checks as `str | None`). Passing `post_processor=None` types
> as `Any` (raw, unvalidated value). A custom `post_processor` types as that callable's own return type.

> **Passing no `exp`:** the default `validate()` post-processor treats a missing `exp` as "accept
> any type" -- it does not fail. Pass `exp=<type>` to add an isinstance check, or
> `post_processor=None` to bypass validation entirely and get the raw match.

**Example:**

```python
data = {
    'response': {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'},
        ]
    }
}

# Extract nested value
name = dig(data, path='response.users[0].name', exp=str)
# Returns: 'Alice'

# Extract with validation
user = dig(data, path='response.users[1]', exp=dict)
# Returns: {'id': 2, 'name': 'Bob'}

# Extract with custom post-processor (no exp needed -- len() isn't validate())
count = dig(data, path='response.users', post_processor=len)
# Returns: 2

# jmespath's full expression syntax is available -- wildcards, filters, functions, etc.
names = dig(data, path='response.users[*].name', exp=list)
# Returns: ['Alice', 'Bob']

# Fallback chain: try a renamed/optional field first, fall back to the old one
name = dig(data, path=['response.users[0].display_name', 'response.users[0].name'], exp=str)
# Returns: 'Alice'
```

##### `dig()` Behavior Matrix

Every row below is a real `dig()` call, backed by a passing unit test in
`test/unit/parsing/test_parsing.py` -- the test name is the proof, not just a claim. This isn't
every possible combination of kwargs (that cross product is huge and mostly redundant); it's one
representative call per distinct decision point in `dig()`/`validate()`. `*(unset)*` means the
kwarg wasn't passed (the function's own default applies); `--` means it isn't relevant to that row.

| `src` | `path` | `exp` | `default` | `post_processor` | `pattern` | `validator` | `pop` | Result | Proven by |
|---|---|---|---|---|---|---|---|---|---|
| `{'first': 'a', 'second': ['blah']}` | `'second[0]'` (found) | `str` | *(unset)* | *(unset)* | *(unset)* | *(unset)* | `False` | `'blah'` | `test_should_get_value_from_dict` |
| `['', ['blah']]` | `'[1][0]'` (found) | `str` | `''` | *(unset)* | *(unset)* | *(unset)* | `False` | `'blah'` (default unused -- value was valid) | `test_should_get_value_from_list` |
| `{'a': {'b': 'value'}}` | `'x.y.z'` (missing) | `str` | `'default'` | *(unset)* | *(unset)* | *(unset)* | `False` | `'default'` | `test_should_return_default_on_missing_intermediate_key` |
| `{'items': ['a', 'b', 'c']}` | `'items.invalid_index'` (missing) | `str` | `'default'` | *(unset)* | *(unset)* | *(unset)* | `False` | `'default'` | `test_should_return_default_when_accessing_list_with_string_key` |
| `{'a': {'b': 'value'}}` | `'x.y.z'` (missing) | `str` | *(unset)* | *(unset)* | *(unset)* | *(unset)* | `False` | `None` (no default set) | `test_should_return_none_for_missing_path_with_exp_and_no_default` |
| `{'a': {'b': 'c'}}` | `'x.y.z'` (missing) | *(unset)* | *(unset)* | *(unset)* | *(unset)* | *(unset)* | `False` | `None` (`exp=None` means "anything passes"; the found value already is `None`) | `test_should_handle_get_value_with_invalid_path` |
| `{'key': 'blah'}` | `'key'` (found) | *(unset)* | *(unset)* | *(unset)* | *(unset)* | *(unset)* | `False` | `'blah'` (raw pass-through, no isinstance check) | `test_should_not_crash_when_exp_omitted_from_dig` |
| `{'a': 'not-an-int'}` | `'a'` (found, wrong type) | `int` | *(unset)* | *(unset)* | *(unset)* | *(unset)* | `False` | `None` | `test_should_return_none_for_dig_result_type_mismatch` |
| `{'a': 'not-an-int'}` | `'a'` (found, wrong type) | `int` | `-1` | *(unset)* | *(unset)* | *(unset)* | `False` | `-1` | `test_should_return_default_for_dig_result_type_mismatch` |
| `{'a': 'blah'}` | `'a'` (found, non-type `exp`) | `'str'` | `'fallback'` | *(unset)* | *(unset)* | *(unset)* | `False` | `'fallback'` (garbage `exp` rejected, not raised) | `test_should_return_default_for_dig_with_non_type_expected_type` |
| `{'key': 'raw_value'}` | `'key'` (found) | -- | -- | `None` | -- | -- | `False` | raw value, unvalidated | `test_should_return_raw_value_when_no_post_processor` |
| `{'a': 1}` | `'missing'` (missing) | -- | `'default'` (ignored) | `None` | -- | -- | `False` | `None` (`default` is never consulted -- it's `validate()`'s kwarg, and `validate()` never runs) | `test_should_return_none_for_missing_path_with_no_post_processor` |
| `{'response': {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}}` | `'response.users'` (found) | -- | -- | `len` | -- | -- | `False` | `2` (custom post_processor gets the raw match) | `test_should_use_custom_post_processor_function` |
| `'blah'` | `None` (src is the value) | `str` | *(unset)* | *(unset)* | *(unset)* | custom lambda | `False` | `'blah'` (custom validator overrides isinstance check) | `test_should_get_value_with_passed_validator` |
| `'test_string'` | `None` (src is the value) | `str` | *(unset)* | *(unset)* | *(unset)* | *(unset)* | `False` | the src value itself | `test_should_post_process_source_when_path_is_none` |
| `{'device': {'mac': 'AA:BB:CC:DD:EE:FF'}}` | `'device.mac'` (found) | `str` | *(unset)* | *(unset)* | matching regex | *(unset)* | `False` | matched MAC string | `test_should_validate_dig_result_with_matching_pattern` |
| `{'device': {'mac': 'not-a-mac'}}` | `'device.mac'` (found) | `str` | `'invalid'` | *(unset)* | non-matching regex | *(unset)* | `False` | `'invalid'` | `test_should_return_default_for_dig_result_with_non_matching_pattern` |
| `{'a': 1, 'b': 2}` | `'a'` (found) | `int` | *(unset)* | *(unset)* | -- | -- | `True` | `1`, and `'a'` removed from `src` | `test_should_pop_key_from_dict` |
| `{'items': [{'id': 1}, {'id': 2}]}` | `'items[?id==\`2\`].id'` (found, ambiguous) | `list` | *(unset)* | *(unset)* | -- | -- | `True` (refused) | `[2]`, `src` left unmutated (pop refused + warning logged) | `test_should_refuse_pop_with_ambiguous_jmespath_filter` |
| `{'user': {'name': 'Alice'}}` | `['user.nickname', 'user.name']` (fallback) | `str` | *(unset)* | *(unset)* | -- | -- | `False` | `'Alice'` (first candidate wins) | `test_should_use_first_matching_path_in_fallback_list` |
| `{'user': {'name': 'Alice'}}` | `['user.nickname', 'user.alias']` (fallback, none match) | `str` | *(unset)* | *(unset)* | -- | -- | `False` | `None` | `test_should_return_none_when_no_fallback_path_matches` |
| `{'user': {'name': 'Alice', 'nickname': 'Ali'}}` | `['user.nickname', 'user.name']` (fallback) | `str` | *(unset)* | *(unset)* | -- | -- | `True` | `'Ali'`, only the winning candidate's key removed | `test_should_pop_only_the_winning_fallback_path` |

#### `dig_many(src, paths, **common_kwargs)`

Extract several named fields from `src` in one call.

- **Parameters:**
  - `src` (Mapping | Sequence): Data structure to navigate
  - `paths` (Mapping[str, Any]): Maps an output key to either a `dig()` path (uses
    `common_kwargs`) or a dict of `dig()` kwargs (must include `'path'`) overriding
    `common_kwargs` for just that key
  - `**common_kwargs`: Default `dig()` kwargs (`exp`, `default`, `converter`, `validator`,
    `post_processor`, `pop`) applied to every key that doesn't override them

- **Returns:** A dict with the same keys as `paths`, each value produced by the corresponding `dig()` call

**Example:**

```python
data = {'user': {'name': 'Alice', 'age': '30'}}

fields = dig_many(
    data,
    paths={
        'name': 'user.name',
        'age': {'path': 'user.age', 'exp': int, 'converter': int},
    },
    exp=str,
)
# Returns: {'name': 'Alice', 'age': 30}
```

#### `Digger(path=None, pop=False, post_processor=validate, **kwargs)`

A pre-bound, reusable `dig()` call. Validates/compiles the jmespath expression once at
construction (failing fast on a bad expression instead of on first use), then can be called
like a function against any number of `src` objects without repeating `path`/`exp`/kwargs. A
string `pattern=` kwarg is likewise pre-compiled to a `re.Pattern` at construction time, so
repeated calls don't re-compile the regex.

**Example:**

```python
records = [{'user': {'name': 'Alice'}}, {'user': {'name': 'Bob'}}]

get_name = Digger(path='user.name', exp=str, default='')
[get_name(record) for record in records]
# Returns: ['Alice', 'Bob']
```

#### `resolve(obj, path, default=None, sep='.')` / `Resolver(path, default=None, sep='.')`

`dig()`/`Digger`'s counterpart for arbitrary Python objects instead of JSON-shaped
dicts/lists -- jmespath has no concept of attribute access or method calls, so it can't
reach a plain object's attributes (a dataclass, an ORM model, an `httpx.Response`'s
`.status_code`/`.headers`/`.json()`). `resolve()` walks a dotted path one segment at a
time, trying dict-style lookup, then sequence-index lookup, then `getattr` -- and
auto-calls anything callable it finds along the way, the same variable-resolution
algorithm Django templates use for `{{ obj.attr.method }}`. `Resolver` is the
pre-bound, reusable form, mirroring `Digger`.

**Example:**

```python
from oj_toolkit.parsing import resolve, Resolver

# response has .status_code and .json() -- not a dict
resolve(response, 'status_code')      # 200
resolve(response, 'json.data.id')     # calls response.json(), then digs into the dict
resolve(response, 'missing', default='n/a')  # 'n/a'

get_id = Resolver(path='json.data.id')
[get_id(r) for r in responses]
```

> **`resolve()` and `dig()` are deliberately separate**, not one auto-detecting
> function -- jmespath's dotted-path syntax means dict-key access (with its own
> wildcard/filter/projection grammar), while an attribute-path's dots mean `getattr`
> plus auto-calling. If a `resolve()` call bottoms out at a plain dict (e.g. a parsed
> JSON body), reach for a second `dig()`/`Digger` call to navigate further into it.

### `data` Module

#### `FlexMixin`

Mixin for flexible data handling. Provides dict-like access to instance and class attributes without the rigidity of `@dataclass`.

**Methods:**

- `get(k, default=None)` — Return attribute value by name, or default if not set
- `to_dict()` — Return all non-private attributes (instance + class hierarchy) as a dict

**Example:**

```python
from oj_toolkit.data.flex import FlexMixin

class MyModel(FlexMixin):
    kind: str = 'model'

obj = MyModel(name='Alice', score=42)
obj.get('name')           # 'Alice'
obj.get('missing', 'n/a') # 'n/a'
obj.get('score', 99)      # 42  (falsy-safe — 0, False, '' all work correctly)
obj.to_dict()             # {'kind': 'model', 'name': 'Alice', 'score': 42}
repr(obj)                 # MyModel({'kind': 'model', 'name': 'Alice', 'score': 42})
```

### `logging` Module

#### `configure_logging(service, env='local', level=None)`

Configure the root logger once at application startup.

- **Parameters:**
  - `service` (str): Name of this service/project — appears in every log record
  - `env` (str): Runtime environment. `'local'` → human-readable; anything else → JSON lines. Default: `'local'`
  - `level` (int | str): Log level as `logging.INFO` / `logging.DEBUG` etc., or a name string `'INFO'`/`'DEBUG'`. Falls back to `LOG_LEVEL` env var, then `WARNING`

- **Behavior:**
  - Idempotent — no-op if root logger already has handlers
  - Writes to `sys.stdout`
  - Silences noisy third-party loggers (`urllib3`, `boto3`, `botocore`, `s3transfer`, `requests`) to WARNING

#### `HumanFormatter`

`logging.Formatter` subclass for human-readable local output. Uses `LOG_FORMAT` and `TimeFormats.DATE_AND_TIME`. No color codes — safe for piped/redirected output.

#### `ColoredHumanFormatter`

Subclass of `HumanFormatter` that wraps the level name in ANSI color codes before rendering. The original log record is never mutated (copied per format call).

| Level | Color |
|---|---|
| DEBUG | dim |
| INFO | cyan |
| WARNING | yellow |
| ERROR | red |
| CRITICAL | bold red |

`configure_logging` selects this automatically when `env='local'` and `detect_color_support()` returns True.

#### `JsonFormatter(service, env)`

`logging.Formatter` subclass for structured JSON output. Emits one JSON object per record with fields: `timestamp`, `level`, `logger`, `service`, `env`, `message` (and `exception` if present).

Subclass and override `extra_fields(record) -> dict` to inject additional fields (e.g., `aws_request_id`, `correlation_id`).

#### `timed_generator(log_progress=True, log_progress_label=None, log_progress_interval=10000, log_level=logging.INFO, logger=None)`

Decorator that logs progress and timing for a generator function.

- **Parameters:**
  - `log_progress` (bool): Enable progress logging. Default: True
  - `log_progress_label` (str): Label for progress messages (e.g., "documents"). Default: function name
  - `log_progress_interval` (int): Log progress every N items. Default: 10000
  - `log_level` (int): Logging level (e.g., `logging.INFO`). Default: `logging.INFO`
  - `logger` (logging.Logger): Logger instance. If None, uses root logger — calls `configure_logging` with local defaults if nothing has configured it yet

- **Returns:** Decorated generator

**Example:**

```python
@timed_generator(
    log_progress_label="records",
    log_progress_interval=1000,
    log_level=logging.DEBUG
)
def fetch_records():
    for i in range(50000):
        yield {'id': i}

for record in fetch_records():
    process(record)
```

Logs:
```
Started records at 2024-01-15T10:30:00+00:00
Fetched 1000 records so far
Fetched 2000 records so far
... (every 1000 items)
Ended records at 2024-01-15T10:35:00+00:00
Yielded 50000 records in 0:05:00
```

#### `timed_async_generator(log_progress=True, log_progress_label=None, log_progress_interval=10000, log_level=logging.INFO, logger=None)`

Async version of `timed_generator`. Same parameters and behavior, but for async generators.

**Example:**

```python
@timed_async_generator(
    log_progress_label="items",
    log_progress_interval=500
)
async def fetch_items():
    for i in range(10000):
        yield await api.get_item(i)

async for item in fetch_items():
    await process(item)
```

#### `BroadcastHandler(maxsize=500)`

`logging.Handler` subclass that forwards log records to all active `asyncio.Queue` subscribers. Designed for log-streaming use cases such as SSE endpoints.

- **Parameters:**
  - `maxsize` (int): Maximum queue depth per subscriber. Slow/stalled consumers are dropped rather than blocking the logger. Default: `500`

- **Methods:**
  - `subscribe() → asyncio.Queue[str]` — Register a new client; returns its dedicated queue
  - `unsubscribe(q)` — Deregister a queue (call on client disconnect)
  - `emit(record)` — Formats and delivers the record to all subscriber queues

**Thread-safety note:** `emit()` calls `asyncio.Queue.put_nowait` directly, which is safe when called from the event loop thread (i.e., inside coroutines). If you log from background threads, subclass and use `loop.call_soon_threadsafe` instead.

**Example (FastAPI SSE endpoint):**

```python
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from oj_toolkit.logging import BroadcastHandler

log_broadcast = BroadcastHandler()

@asynccontextmanager
async def lifespan(app):
    logging.getLogger().addHandler(log_broadcast)
    yield
    logging.getLogger().removeHandler(log_broadcast)

app = FastAPI(lifespan=lifespan)

@app.get("/logs")
async def stream_logs():
    q = log_broadcast.subscribe()

    async def _generate():
        try:
            while True:
                msg = await q.get()
                lines = msg.replace("\r\n", "\n").split("\n")
                yield "".join(f"data: {line}\n" for line in lines) + "\n"
        except asyncio.CancelledError:
            pass
        finally:
            log_broadcast.unsubscribe(q)

    return StreamingResponse(_generate(), media_type="text/event-stream")
```

### `asynchronous` Module

#### `a_chunks(chunk_size, async_iterable)`

Yield successive fixed-size chunks from an async iterable.

- **Parameters:**
  - `chunk_size` (int): Maximum number of items per chunk
  - `async_iterable` (AsyncIterator[T]): The async iterable to chunk

- **Returns:** `AsyncGenerator[List[T], None]` — yields lists of up to `chunk_size` elements. The final chunk may be smaller if the iterable is exhausted.

**Example:**

```python
from oj_toolkit.asynchronous import a_chunks

async def process():
    async def records():
        for i in range(250):
            yield i

    async for batch in a_chunks(100, records()):
        await bulk_insert(batch)  # batches of 100, 100, 50
```

#### `@async_timeout(seconds=10, error_message=None)`

Decorator that raises `TimeoutError` if the wrapped coroutine runs longer than `seconds`. Built on `asyncio.timeout()`, so the inner coroutine is actually cancelled (not just abandoned) once the deadline passes.

- **Parameters:**
  - `seconds` (float): Maximum time to wait for the coroutine to complete. Default: `10`
  - `error_message` (str): Message for the raised `TimeoutError`. Default: the OS-provided `ETIME` message

**Example:**

```python
from oj_toolkit.asynchronous import async_timeout
import asyncio

@async_timeout(seconds=2)
async def slow_call():
    await asyncio.sleep(5)

try:
    await slow_call()
except TimeoutError as e:
    print(f'gave up waiting: {e}')
```

> **Note:** `asyncio.timeout()` can also be used directly as an `async with` block to
> share one deadline across several awaits, rather than bounding a single named
> function. Reach for that when you need more than "time out this one call".
> Requires Python 3.11+ -- this project's minimum supported version.

### `timing` Module

#### `@timeout(seconds=10, error_message=None)`

Decorator that raises `TimeoutError` if the wrapped (blocking/synchronous) call runs longer than `seconds`. Runs the call on a daemon thread and waits up to `seconds` for it to finish -- works identically on every platform and from any calling thread, unlike a `signal.alarm`-based timeout (Unix-only, main-thread-only, and unavailable on Windows entirely).

- **Parameters:**
  - `seconds` (float): Maximum time to wait for the wrapped call to complete. Default: `10`
  - `error_message` (str): Message for the raised `TimeoutError`. Default: the OS-provided `ETIME` message

**Example:**

```python
from oj_toolkit.timing import timeout
import time

@timeout(seconds=2)
def slow_call():
    time.sleep(5)

try:
    slow_call()
except TimeoutError as e:
    print(f'gave up waiting: {e}')
```

> **Limitation:** Python cannot forcibly kill a running thread. Past the deadline,
> `timeout()` raises and returns control to the caller immediately, but the wrapped
> function keeps running to completion on its worker thread in the background -- it's
> abandoned, not aborted. The thread is created with `daemon=True` so an abandoned call
> never blocks interpreter shutdown. Use this to stop *waiting* on a slow call, not to
> terminate runaway or CPU-bound work. For coroutines, use `async_timeout` instead,
> which actually cancels the inner call.

### `ops` Module

Small, composable "op" classes that nest to build a data-processing/logic chain, and can
equally be built from a declarative spec dict via `compile()`. Two "levels":

- **Item-level ops** (`__call__(self, item) -> Any`): conditions (`And`, `Or`, `Xor`,
  `Not`, `In`, `Eq`, `Ne`, `Gt`, `Lt`, `Ge`, `Le`, `Exists`), control flow (`When`, `Map`,
  `Sequence`), structure manipulation (`Extract`, `Resolve`, `MapField`, `Broadcast`,
  `Fanout`, `Merge`), key/value reshaping (`Pick`, `Omit`, `Rename`, `SetField`), time
  (`Now`, `Elapsed`), and `Glom` (an optional-dependency escape hatch to the
  [glom](https://glom.readthedocs.io/) library's spec language -- `pip install
  'oj-toolkit[glom]'`).
- **Stream-level ops** (`__call__(self, iterable) -> Iterator[Any]`): `Iter` (the generic
  lift of any single-item callable, analogous to Python's `map()` builtin separating "the
  function" from "the iteration machinery"), `Filter`, `FlatMap`, `GroupBy`, `Join`, `Zip`,
  and `Pipeline` (chains other `StreamOp`s in sequence -- the stream-level counterpart to
  `Sequence`).

Composition is plain nested constructor calls -- no operator overloading -- which maps
1:1 onto a declarative spec. Every comparison's `input=` accepts either a jmespath path
or any callable/Op, evaluated fresh on every call -- see the full guide in
`oj_toolkit/ops/README.md` for the design rationale and every op's reference.

**Example: nested Python construction**

```python
from oj_toolkit.ops import Filter, In, Iter

pipeline = Iter(fn=str.upper)
list(pipeline(['a', 'b']))  # ['A', 'B']

only_ok = Filter(condition=In(input='status', value=['ok', 'warn']))
list(only_ok([{'status': 'ok'}, {'status': 'fail'}]))  # [{'status': 'ok'}]
```

**Example: the same pipeline from a declarative spec**

```python
from oj_toolkit.ops import compile as compile_ops

spec = {'type': 'filter', 'condition': {'type': 'in', 'input': 'status', 'value': ['ok', 'warn']}}
op = compile_ops(spec)
list(op([{'status': 'ok'}, {'status': 'fail'}]))  # [{'status': 'ok'}]
```

**Example: fan-out a parent record's children ("enclosure with blades")**

```python
from oj_toolkit.ops import Broadcast, FlatMap

expand_blades = FlatMap(op=Broadcast(
    children_path='blades',
    fields={'enclosure_id': 'enclosure_id', 'location': 'location'},
))
list(expand_blades([{
    'enclosure_id': 'abc', 'location': 'rack1',
    'blades': [{'serial': 'b1'}, {'serial': 'b2'}],
}]))
# [{'enclosure_id': 'abc', 'location': 'rack1', 'serial': 'b1'},
#  {'enclosure_id': 'abc', 'location': 'rack1', 'serial': 'b2'}]
```

> **Note:** `compile` shadows the `compile()` builtin. Import it as
> `from oj_toolkit.ops import compile as compile_ops` (or use the pre-aliased
> `oj_toolkit.compile_ops` re-export) so it doesn't shadow the builtin in your own
> module's scope.

## Development

### Setup

```bash
git clone https://github.com/ownjoo/ownjoo-toolkit.git
cd ownjoo-toolkit
pip install -e ".[dev]"
```

### Running Tests

```bash
python -m pytest test/ -v
```

With coverage:

```bash
python -m pytest test/ --cov=oj_toolkit --cov-report=html
```

### Code Style

This project uses `black` for formatting and `ruff` for linting.

```bash
# Format code
black oj_toolkit/

# Check formatting
black --check oj_toolkit/

# Lint
ruff check oj_toolkit/
```

### Testing Guidelines

- Write tests for all new functionality
- Aim for >80% test coverage
- Use pytest for all test files
- See `test/unit/` for examples

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Code standards and conventions
- Testing requirements
- Commit message format
- Pull request process

## Standards

This library follows the ownjoo standards defined in [CLAUDE.md](https://github.com/ownjoo/claude/blob/main/CLAUDE.md).

Key principles:
- **Simplicity First** — Write the simplest code that solves the problem
- **Pragmatic Testing** — Use integration tests for real dependencies, unit tests for isolation
- **Explicit Commits** — Use conventional commits (feat/fix/refactor/docs/test/chore)
- **Security by Default** — No OWASP Top 10 vulnerabilities, review before commit

## Versioning

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backward-compatible functionality additions
- **PATCH** version for backward-compatible bug fixes

All changes to the public API should include thorough documentation and example usage.

## License

[See LICENSE file]

## Support

For issues, questions, or contributions, please use the GitHub repository:
- Issues: [github.com/ownjoo/ownjoo-toolkit/issues](https://github.com/ownjoo/ownjoo-toolkit/issues)
- Pull Requests: [github.com/ownjoo/ownjoo-toolkit/pulls](https://github.com/ownjoo/ownjoo-toolkit/pulls)
