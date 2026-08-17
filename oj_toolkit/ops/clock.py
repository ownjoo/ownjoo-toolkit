"""Time-based item-level ops: Now, Elapsed.

Neither op is a condition by itself -- they're value-producing legos meant to plug
into input= on a comparison (see conditions.py), the same way any other callable/Op
can: Gt(input=Elapsed(since='created_at'), value=300) reads as "more than 300 seconds
have elapsed since created_at."
"""

import time
from typing import Any

from oj_toolkit.ops.base import ItemOp, PathOrCallable
from oj_toolkit.ops.registry import register
from oj_toolkit.parsing import Digger


@register("now")
class Now(ItemOp):
    """Ignores the item; returns the current time (epoch seconds, time.time())."""

    def __call__(self, item: Any) -> float:
        return time.time()


@register("elapsed")
class Elapsed(ItemOp):
    """Seconds elapsed (via time.time()) since a timestamp field or nested op.

    Attributes:
        since: A jmespath path/bare int shorthand/fallback list (extracted via
            Digger, expected to resolve to epoch seconds), or any callable/Op --
            called directly against the item on every evaluation instead.
    """

    def __init__(self, since: PathOrCallable, **dig_kwargs: Any) -> None:
        self.since = since
        self.dig_kwargs = dig_kwargs
        self._since_fn = since if callable(since) else Digger(path=since, **dig_kwargs)

    def __call__(self, item: Any) -> float:
        return time.time() - float(self._since_fn(item))

    def clone(self, **overrides: Any) -> "Elapsed":
        kwargs = {"since": self.since, **self.dig_kwargs, **overrides}
        return Elapsed(**kwargs)
