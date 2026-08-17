"""Item-level control-flow and transform ops: When, Map, Sequence."""

from typing import Any, Callable

from oj_toolkit.ops.base import ItemOp, Op
from oj_toolkit.ops.registry import register


@register("when")
class When(ItemOp):
    """Branch between two item-level ops based on a condition.

    Attributes:
        condition: An item-level op returning a truthy/falsy result.
        then: The op applied when condition(item) is truthy.
        otherwise: The op applied when condition(item) is falsy. Default: None, meaning
            the item passes through unchanged -- the least surprising default for a data
            pipeline ("if X, do Y; otherwise leave it alone").
    """

    def __init__(self, condition: Op, then: Op, otherwise: Op | None = None) -> None:
        self.condition = condition
        self.then = then
        self.otherwise = otherwise

    def __call__(self, item: Any) -> Any:
        if self.condition(item):
            return self.then(item)
        if self.otherwise is None:
            return item
        return self.otherwise(item)


@register("map")
class Map(ItemOp):
    """Apply a plain callable to a single item -- the item-level "transform" leaf.

    Analogous to the function you'd pass to Python's map() builtin. fn need not be an Op;
    any callable works (e.g. str.upper, json.loads, a lambda).
    """

    def __init__(self, fn: Callable[[Any], Any]) -> None:
        self.fn = fn

    def __call__(self, item: Any) -> Any:
        return self.fn(item)


@register("sequence")
class Sequence(ItemOp):
    """Apply a list of item-level ops to an item in order, threading the result through
    each stage. A flat, linear escape hatch for chains where nested constructors
    (A(B(C(x)))) would read inside-out and become unreadable.
    """

    def __init__(self, ops: list[Op]) -> None:
        self.ops = ops

    def __call__(self, item: Any) -> Any:
        for op in self.ops:
            item = op(item)
        return item
