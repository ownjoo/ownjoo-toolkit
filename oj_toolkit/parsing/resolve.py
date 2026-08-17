"""Attribute/method resolution for arbitrary Python objects.

dig()/Digger (see oj_toolkit.parsing.types) navigate JSON-shaped data via jmespath --
dicts, lists, scalars. jmespath has no concept of attribute access or method calls, so
it can't reach into a plain Python object (a dataclass, an ORM model, an httpx.Response
with .status_code/.headers/.json()). resolve() is dig()'s counterpart for that case: a
dotted path walked one segment at a time, trying dict/mapping lookup, then
sequence-index lookup, then attribute access -- auto-calling anything callable it finds
along the way, the same variable-resolution algorithm Django templates use for
`{{ obj.attr.method }}`.

The two aren't merged into one function on purpose: jmespath's dotted-path syntax means
something different (dict key access, with its own wildcard/filter/projection grammar)
than an attribute-path's dots do, and auto-detecting which was intended invites
ambiguity. If a resolve() call bottoms out at a plain dict (e.g. a parsed JSON body from
.json()), reach for a second dig()/Digger call to navigate further into it.
"""

from collections.abc import Mapping, Sequence
from typing import Any


def resolve(obj: Any, path: str, default: Any = None, sep: str = ".") -> Any:
    """Walk a dotted path over an arbitrary Python object, auto-calling anything
    callable found along the way.

    For each path segment, in order: dict-style lookup (if the current value is a
    Mapping and the segment is a key in it), then sequence-index lookup (if the
    current value is a Sequence, not a str, and the segment parses as an int), then
    attribute lookup via getattr. After resolving a segment, if the result is
    callable, it's called with no arguments before moving on to the next segment.

    Args:
        obj: The object to navigate -- a dict, a list, or any Python object
            (dataclass, ORM model, httpx.Response, etc).
        path: A sep-separated path, e.g. 'status_code' or 'json.data.id'.
        default: Returned if any segment can't be resolved (AttributeError, KeyError,
            IndexError, or a TypeError from an unindexable/uncallable value).
            Default: None.
        sep: Path segment separator. Default: '.'.

    Returns:
        The resolved (and auto-called, where applicable) value, or default.

    Example:
        >>> class Response:
        ...     status_code = 200
        ...     def json(self):
        ...         return {'data': {'id': 1}}
        >>> resolve(Response(), 'status_code')
        200
        >>> resolve(Response(), 'json.data.id')
        1
        >>> resolve(Response(), 'missing.path', default='n/a')
        'n/a'
    """
    current = obj
    for segment in path.split(sep):
        try:
            if isinstance(current, Mapping) and segment in current:
                current = current[segment]
            elif (
                isinstance(current, Sequence)
                and not isinstance(current, str)
                and segment.lstrip("-").isdigit()
            ):
                current = current[int(segment)]
            else:
                current = getattr(current, segment)
        except (AttributeError, KeyError, IndexError, TypeError):
            return default
        if callable(current):
            current = current()
    return current


class Resolver:
    """A pre-bound, reusable resolve() call -- build once, invoke against many objects.

    Example:
        >>> get_status = Resolver(path='status_code')
        >>> responses = []  # doctest: +SKIP
        >>> [get_status(r) for r in responses]  # doctest: +SKIP
    """

    def __init__(self, path: str, default: Any = None, sep: str = ".") -> None:
        self.path = path
        self.default = default
        self.sep = sep

    def __call__(self, obj: Any) -> Any:
        return resolve(obj, path=self.path, default=self.default, sep=self.sep)

    def __repr__(self) -> str:
        return f"Resolver(path={self.path!r})"
