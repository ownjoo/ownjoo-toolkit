"""Stream-level ops that are one-in/N-out per item: Iter, Filter, FlatMap.

Each takes an iterable and returns a generator. Iter is the generic lift from a single
item-level callable to a stream op (analogous to Python's map() builtin); Filter and
FlatMap change cardinality (drop items, or expand one item into several) and so can't be
expressed as an Iter-lifted item op.
"""

from collections.abc import Iterable, Iterator
from typing import Any, Callable

from oj_toolkit.ops.base import Op, StreamOp
from oj_toolkit.ops.registry import register


@register("iter")
class Iter(StreamOp):
    """Adapt a single-item callable to run over an iterable, one-in/one-out.

    fn need not be an Op -- any callable works (an Op instance qualifies since it's
    callable, but so does str.upper or a lambda).
    """

    def __init__(self, fn: Callable[[Any], Any]) -> None:
        if not callable(fn):
            raise TypeError("Iter requires an fn callable")
        self.fn = fn

    def __call__(self, i: Iterable[Any]) -> Iterator[Any]:
        for x in i:
            yield self.fn(x)


@register("filter")
class Filter(StreamOp):
    """Yield only the items for which condition(item) is truthy."""

    def __init__(self, condition: Op) -> None:
        self.condition = condition

    def __call__(self, i: Iterable[Any]) -> Iterator[Any]:
        for item in i:
            if self.condition(item):
                yield item


@register("flat_map")
class FlatMap(StreamOp):
    """Apply op to each item, expecting an iterable result, and yield from it.

    One input item can expand into zero, one, or many output items -- e.g. Broadcast
    (see structure.py) turns one parent record into a list of parent+child records.
    """

    def __init__(self, op: Op) -> None:
        self.op = op

    def __call__(self, i: Iterable[Any]) -> Iterator[Any]:
        for item in i:
            yield from self.op(item)
