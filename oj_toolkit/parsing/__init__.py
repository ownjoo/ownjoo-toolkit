"""Type validation and data parsing utilities.

Provides functions for:
- Converting strings to lists with custom separators
- Parsing datetime values from multiple formats
- Validating and converting values with custom validators and converters
- Extracting and validating nested values from dicts/lists (jmespath-backed)
- Resolving attribute/method paths on arbitrary Python objects (dig()'s counterpart
  for non-dict/list data, e.g. httpx.Response)
- Stripping an HTML document down to its title + visible text (for the case where an
  API redirected to an HTML page instead of returning the expected payload)
"""

from oj_toolkit.parsing.html import strip_html
from oj_toolkit.parsing.resolve import Resolver, resolve
from oj_toolkit.parsing.types import Digger, dig, dig_many, get_datetime, str_to_list, validate

__all__ = [
    "validate",
    "get_datetime",
    "dig",
    "dig_many",
    "Digger",
    "str_to_list",
    "resolve",
    "Resolver",
    "strip_html",
]
