"""ownjoo shared utilities library.

Centralized utilities for all ownjoo projects, including:
- Type validation and data parsing (parsing module)
- Progress logging for generators (logging module)
- Terminal and console output utilities (console module)
  - Basic output and colors
  - Formatted tables, boxes, and status displays
- Asynchronous utilities (asynchronous module, in development)
- Wall-clock timeout decorators for sync and async calls (timing module)
- Diagnostics: exception-visibility hooks so no async/thread/finalizer
  error can disappear silently (diagnostics module)

Usage:
    from oj_toolkit import validate, get_datetime, str_to_list, dig, dig_many, Digger
    from oj_toolkit import timed_generator, timed_async_generator
    from oj_toolkit import Output, Color, ColoredText
    from oj_toolkit import Table, Box, status_line, progress_bar
    from oj_toolkit import install_exception_visibility
    from oj_toolkit import timeout, async_timeout
"""

from oj_toolkit.asynchronous import async_timeout
from oj_toolkit.console import (
    Box,
    Color,
    ColoredText,
    Output,
    Table,
    in_box,
    progress_bar,
    status_badge,
    status_line,
    status_wrapped,
    tabulated,
)
from oj_toolkit.diagnostics import install_exception_visibility
from oj_toolkit.logging import timed_async_generator, timed_generator
from oj_toolkit.parsing import Digger, dig, dig_many, get_datetime, str_to_list, validate
from oj_toolkit.timing import timeout

__all__ = [
    'timed_async_generator',
    'timed_generator',
    'install_exception_visibility',
    'validate',
    'get_datetime',
    'dig',
    'dig_many',
    'Digger',
    'str_to_list',
    'Output',
    'Color',
    'ColoredText',
    'Table',
    'tabulated',
    'Box',
    'in_box',
    'status_line',
    'progress_bar',
    'status_badge',
    'status_wrapped',
    'timeout',
    'async_timeout',
]
