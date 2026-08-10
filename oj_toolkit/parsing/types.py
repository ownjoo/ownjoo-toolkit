"""Parsing and type validation utilities for common data conversions.

This module provides functions to safely parse and validate values, including:
- String to list conversion with custom separators
- Datetime parsing from multiple formats
- Nested value extraction from dicts/lists
- Generic validation with custom converters and validators
"""

import logging
import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from functools import lru_cache
from typing import Any, Callable, Type, TypeVar, overload

import jmespath

from oj_toolkit.parsing.consts import DEFAULT_SEPARATOR, TimeFormats

T = TypeVar('T')
R = TypeVar('R')

logger = logging.getLogger(__name__)


def DEFAULT_CONVERTER(value: Any, *args: Any, **kwargs: Any) -> Any:  # pylint: disable=invalid-name,unused-argument
    return value


def DEFAULT_VALIDATOR(value: Any, expected_type: Any, *args: Any, **kwargs: Any) -> bool:  # pylint: disable=invalid-name,unused-argument
    return expected_type is None or (
        isinstance(expected_type, (type, tuple)) and isinstance(value, expected_type)
    )


def str_to_list(v: str | None = None, separator: str = DEFAULT_SEPARATOR) -> list[str] | None:
    """Convert a string to a list by splitting on a separator.

    Args:
        v: The string to split. If not a string, returns unchanged.
        separator: The delimiter to split on (default: comma). Empty string returns value unchanged.

    Returns:
        A list of strings if v is a non-empty string with valid separator, otherwise the original value.

    Example:
        >>> str_to_list('a,b,c')
        ['a', 'b', 'c']
        >>> str_to_list('a;b;c', separator=';')
        ['a', 'b', 'c']
        >>> str_to_list(None)
        None
    """
    if not isinstance(v, str) or separator == '':
        return v
    if not isinstance(separator, str):
        separator = DEFAULT_SEPARATOR
    return v.split(separator)


def get_datetime(
        v: datetime | float | str | None = None,
        format_str: str | None = None,
) -> datetime | None:
    """Parse a value into a datetime object from multiple input formats.

    Supports parsing from:
    - datetime objects (returned as-is)
    - Numeric timestamps (seconds since epoch)
    - Strings matching known time formats (ISO 8601, HTTP date, custom format)

    Args:
        v: The value to parse. Can be None, datetime, float/int timestamp, or string.
        format_str: Optional custom datetime format string (strptime format). If provided, attempts parsing with this
        format first.

    Returns:
        A datetime object if parsing succeeds, otherwise None.

    Supported Formats:
        - ISO 8601: 'YYYY-MM-DDTHH:MM:SS'
        - HTTP: 'Sun, 06 Nov 1994 08:49:37 GMT'
        - Date and time: 'YYYY/MM/DD HH:MM:SS'
        - Custom format via format_str parameter

    Example:
        >>> get_datetime('2024-01-15T10:30:00')
        datetime.datetime(2024, 1, 15, 10, 30)
        >>> get_datetime(1234567890)
        datetime.datetime(2009, 2, 13, 23, 31, 30)
        >>> get_datetime('Sun, 06 Nov 1994 08:49:37 GMT')
        datetime.datetime(1994, 11, 6, 8, 49, 37)
    """
    result: datetime | None = None
    try:
        if isinstance(v, datetime):
            result = v
        elif isinstance(v, (float, int)):  # if number treat as a timestamp (seconds from epoch)
            result = datetime.fromtimestamp(v)
        elif isinstance(v, str) and isinstance(format_str, str):
            result = datetime.strptime(v, format_str)
        elif isinstance(v, str):
            for time_format in TimeFormats:  # if str try to parse the str from a known format
                try:
                    result = datetime.strptime(v, time_format.value)
                except Exception:
                    # Silently try next format instead of logging each failure
                    continue
        else:
            logger.warning(f'Unusable {v=}, {format_str=}. Returning {result=}')
    except Exception as exc:
        logger.debug(f'Failed to parse {v=}: {exc}')
    return result


def validate(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        v: Any,
        exp: Type[T] = None,
        default: T | None = None,
        converter: Callable = None,
        validator: Callable | None = DEFAULT_VALIDATOR,
        pattern: str | re.Pattern | None = None,
        **kwargs
) -> T | None:
    """Validate and optionally convert a value with a custom converter and validator.

    This is a generic validation utility that:
    1. Converts the value using a converter function (with automatic selection for common types)
    2. Validates the result using a validator function
    3. Optionally checks the result against a regex pattern (str results only)
    4. Returns the result if valid, otherwise returns the default value

    Args:
        v: The value to validate.
        exp: Expected type of the value. If None, no type conversion or isinstance check is
            attempted (DEFAULT_VALIDATOR passes any value through unchanged).
        default: The value to return if validation fails or v is None. Default: None.
        converter: Custom converter function. If None, one is selected based on exp:
            - exp=list: uses str_to_list
            - exp=datetime: uses get_datetime
            - otherwise: uses DEFAULT_CONVERTER (pass-through)
        validator: Custom validator function(result, exp, **kwargs) -> bool.
            If None, uses DEFAULT_VALIDATOR (isinstance check).
        pattern: Optional regex (string or compiled re.Pattern) the result must fully match
            via re.fullmatch. Only applied when the (converted, validated) result is a str;
            checked after conversion/validation succeed. On mismatch, returns default.
        **kwargs: Additional arguments passed to converter and validator functions.

    Returns:
        The converted and validated value, or the default value if validation fails.
        Returns None if no default is specified and validation fails.

    Example:
        >>> validate('123', exp=int, converter=int)
        123
        >>> validate('invalid', exp=int, default=0)
        0
        >>> validate('a,b,c', exp=list)
        ['a', 'b', 'c']
        >>> validate('AA:BB:CC:DD:EE:FF', exp=str, pattern=r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}')
        'AA:BB:CC:DD:EE:FF'
    """
    result: Any = v
    is_valid_result: bool = False

    # check pre-defined converters
    if not callable(converter):
        if exp is list:
            converter = str_to_list
        elif exp is datetime:
            converter = get_datetime
        else:
            converter = DEFAULT_CONVERTER  # pass through

    # convert values as needed
    conversion_succeeded = True
    try:
        result = converter(v, **kwargs)
    except Exception as exc_str:
        logger.debug(f'Failed to parse {v=} with converter {converter}: {exc_str}', exc_info=True)
        conversion_succeeded = False

    # check validator (only if conversion succeeded)
    if conversion_succeeded:
        if not callable(validator):
            validator = DEFAULT_VALIDATOR

        try:
            is_valid_result = validator(result, exp, **kwargs)
        except Exception as exc_validation:
            logger.debug(f'Failed validation: {validator=}: {exc_validation=}', exc_info=True)

    if is_valid_result and pattern is not None and isinstance(result, str):
        compiled_pattern = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern)
        if not compiled_pattern.fullmatch(result):
            is_valid_result = False

    return result if is_valid_result else default


_JMESPATH_INSTALL_HINT = "jmespath is not installed. Install it with: pip install 'oj-toolkit[jmespath]'"

# Characters that make a jmespath expression ambiguous to pop from (filters, wildcards,
# pipes, flatten/multi-select, raw-string literals) -- pop is refused if any are present.
_JMESPATH_POP_UNSAFE_CHARS = frozenset('*?|&`{}')

_JMESPATH_TERMINAL_RE = re.compile(
    r'(?:^|\.)"((?:[^"\\]|\\.)*)"$'
    r'|(?:^|\.)([A-Za-z_][A-Za-z0-9_]*)$'
    r'|\["((?:[^"\\]|\\.)*)"]$'
    r'|\[(\d+)]$'
)


@lru_cache(maxsize=256)
def _compile_jmespath(expr: str) -> Any:
    """Compile (and cache) a jmespath expression string.

    This cache is process-global and shared by every dig()/Digger call, keyed on the
    expression string -- a bare dig() call already avoids recompiling a repeated path, not
    just Digger. Capped at 256 distinct expressions (LRU-evicted); Digger's up-front compile
    call at construction populates this same cache rather than maintaining its own.
    """
    return jmespath.compile(expr)


def _jmespath_terminal(expr: str) -> tuple[str | None, str | int] | None:
    """Split a jmespath expression into (parent_expr, terminal_key) for pop, if it's safe to do so.

    Returns None if the expression's last segment can't be unambiguously isolated
    (e.g. it ends in a filter, wildcard, or projection) -- pop is refused in that case.
    """
    if any(c in _JMESPATH_POP_UNSAFE_CHARS for c in expr):
        return None
    match = _JMESPATH_TERMINAL_RE.search(expr)
    if not match:
        return None
    quoted, identifier, bracket_quoted, index = match.groups()
    parent_expr = expr[:match.start()] or None
    if index is not None:
        return parent_expr, int(index)
    raw_key = quoted if quoted is not None else (identifier if identifier is not None else bracket_quoted)
    return parent_expr, raw_key.replace('\\"', '"').replace('\\\\', '\\')


def _path_to_expr(path: int | str) -> str:
    """Normalize a single path segment (int shorthand or raw jmespath string) into an expression."""
    if isinstance(path, str):
        return path
    if isinstance(path, int) and not isinstance(path, bool):
        return f'[{path}]'
    raise TypeError(f'path must be an int, str, a list of these, or None; got {type(path).__name__}')


def _dig_expr(src: Mapping | Sequence, expr: str, pop: bool) -> Any:
    """Evaluate one jmespath expression against src, optionally popping the terminal match."""
    result = _compile_jmespath(expr).search(src)
    if pop and result is not None:
        terminal = _jmespath_terminal(expr)
        if terminal is None:
            logger.warning(f'Refusing to pop ambiguous jmespath expression: {expr=}')
        else:
            parent_expr, keydex = terminal
            parent = src if parent_expr is None else _compile_jmespath(parent_expr).search(src)
            try:
                del parent[keydex]
            except (IndexError, KeyError, TypeError) as exc_pop:
                logger.warning(f'Failed to pop {keydex=} from {parent=}: {exc_pop}')
    return result


@overload
def dig(  # pylint: disable=too-many-arguments
        src: Mapping | Sequence,
        path: int | str | list[int | str] | None = None,
        pop: bool = False,
        *,
        exp: Type[T],
        default: T | None = None,
        converter: Callable[..., Any] | None = None,
        validator: Callable[..., bool] | None = DEFAULT_VALIDATOR,
        post_processor: Callable[..., Any] = validate,
        **kwargs: Any,
) -> T | None: ...


@overload
def dig(
        src: Mapping | Sequence,
        path: int | str | list[int | str] | None = None,
        pop: bool = False,
        post_processor: None = None,
        **kwargs: Any,
) -> Any: ...


@overload
def dig(
        src: Mapping | Sequence,
        path: int | str | list[int | str] | None = None,
        pop: bool = False,
        post_processor: Callable[..., R] = validate,
        **kwargs: Any,
) -> R | None: ...


def dig(
        src: Mapping | Sequence,
        path: int | str | list[int | str] | None = None,
        pop: bool = False,
        post_processor: Callable[..., Any] | None = validate,
        **kwargs: Any,
) -> Any:
    """Extract and post-process a value from a nested data structure.

    Navigates through nested dicts and lists using a jmespath expression string (or a
    bare int as shorthand for a single top-level index), then post-processes the result
    with a callable (default: validate).

    Args:
        src: A dict or list to navigate. If path is None, treated as a single value to post-process.
        path: A jmespath expression string (e.g. 'users[0].name', 'users[*].name'), a bare
            int as shorthand for a single top-level index (e.g. 1 is equivalent to '[1]'),
            a list of these tried in order as fallbacks (the first one whose result is not
            None wins -- useful for optional/renamed fields), or None to treat src itself as
            the value to post-process.
        pop: If True, delete the terminal key/index from its container after extracting the value.
            Mutates src in place. Default: False. Only honored when the winning expression's
            terminal segment is an unambiguous key/index (no wildcards, filters, or
            projections) -- otherwise it's refused with a warning and the value is still
            returned unpopped.
        post_processor: Callable to post-process the found value. Default: validate().
            If None, the raw value is returned without post-processing.
        **kwargs: Additional arguments passed to post_processor function. Pass exp=<type> to have
            the default validate() post-processor -- and this function's inferred return type --
            narrow to Optional[<type>] instead of Any.

    Returns:
        The post-processed value, or None if extraction fails or no post-processor is specified.

    Example:
        >>> src = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
        >>> dig(src, path='users[0].name', exp=str)
        'Alice'
        >>> dig(src, path='users[1].name', exp=str)  # return type inferred as str | None
        'Bob'
        >>> dig(src, path='users[*].name', exp=list)
        ['Alice', 'Bob']
        >>> dig(src, path=['users[0].nickname', 'users[0].name'], exp=str)  # fallback chain
        'Alice'
        >>> dig(src, path='users[0].name', pop=True, exp=str)  # removes 'name' from src['users'][0]
        'Alice'
        >>> src['users'][0]
        {}
    """
    if path is None:
        result = src
    elif isinstance(path, (list, tuple)):
        result = None
        for candidate in path:
            candidate_result = _dig_expr(src, _path_to_expr(candidate), pop)
            if candidate_result is not None:
                result = candidate_result
                break
    else:
        result = _dig_expr(src, _path_to_expr(path), pop)

    # Always run the post-processor -- even on a missing/None result -- so it can apply
    # its own default handling (validate() already treats v=None as failing an isinstance
    # check and falls back to kwargs['default']). Skipping post_processor entirely is
    # reserved for the explicit post_processor=None "give me the raw value" case.
    if callable(post_processor):
        return post_processor(result, **kwargs)
    return result


def dig_many(
        src: Mapping | Sequence,
        paths: Mapping[str, Any],
        **common_kwargs: Any,
) -> dict[str, Any]:
    """Extract several named fields from src in one call.

    Args:
        src: A dict or list to navigate.
        paths: Maps an output key to either a dig() path (int/str/list, using common_kwargs
            for exp/default/etc.) or a mapping of dig() kwargs (must include 'path') to
            override common_kwargs for that one key.
        **common_kwargs: Default dig() kwargs (exp, default, converter, validator,
            post_processor, pop) applied to every key that doesn't override them.

    Returns:
        A dict with the same keys as paths, each value produced by the corresponding dig() call.

    Example:
        >>> src = {'user': {'name': 'Alice', 'age': '30'}}
        >>> dig_many(
        ...     src,
        ...     paths={'name': 'user.name', 'age': {'path': 'user.age', 'exp': int, 'converter': int}},
        ...     exp=str,
        ... )
        {'name': 'Alice', 'age': 30}
    """
    result: dict[str, Any] = {}
    for key, spec in paths.items():
        call_kwargs = {**common_kwargs, **spec} if isinstance(spec, Mapping) else {**common_kwargs, 'path': spec}
        result[key] = dig(src, **call_kwargs)
    return result


class Digger:
    """A pre-bound, reusable dig() call -- build once, invoke against many src objects.

    Validates/compiles the path up front (failing fast on a bad jmespath expression
    instead of on first use) and avoids re-passing the same path/exp/post_processor/kwargs
    on every call. A string `pattern=` kwarg is likewise pre-compiled to a re.Pattern here
    so repeated calls don't re-compile the regex on every invocation.

    Example:
        >>> get_name = Digger(path='user.name', exp=str, default='')
        >>> [get_name(record) for record in records]  # doctest: +SKIP
    """

    def __init__(
            self,
            path: int | str | list[int | str] | None = None,
            pop: bool = False,
            post_processor: Callable[..., Any] | None = validate,
            **kwargs: Any,
    ) -> None:
        self.path = path
        self.pop = pop
        self.post_processor = post_processor
        if isinstance(kwargs.get('pattern'), str):
            kwargs['pattern'] = re.compile(kwargs['pattern'])
        self.kwargs = kwargs
        for candidate in (path if isinstance(path, (list, tuple)) else [path]):
            if candidate is not None:
                _compile_jmespath(_path_to_expr(candidate))

    def __call__(self, src: Mapping | Sequence) -> Any:
        return dig(src, path=self.path, pop=self.pop, post_processor=self.post_processor, **self.kwargs)

    def __repr__(self) -> str:
        return f'Digger(path={self.path!r}, pop={self.pop!r})'
