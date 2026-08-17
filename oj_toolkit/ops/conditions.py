"""Boolean condition ops: comparisons against an extracted field, and logic combinators.

Every comparison op extracts a value from the item via an input=, then compares it to
value=. input= is either a jmespath path (extracted via dig()/Digger, see
oj_toolkit.parsing.types) or any callable/Op, evaluated fresh against the item on every
call -- the same str-or-callable pattern GroupBy.key already uses in group.py. The
callable form is what lets a dynamic value (e.g. Elapsed(since=...) in clock.py, or
Resolve(path=...) in structure.py for non-dict objects) plug into any comparison.
"""

import functools
import operator
from typing import Any

from oj_toolkit.ops.base import ItemOp, Op, PathOrCallable
from oj_toolkit.ops.registry import register
from oj_toolkit.parsing import Digger, dig


class _Comparison(ItemOp):  # pylint: disable=abstract-method
    """Shared base for ops that extract a field via input= and compare it to value.

    Not registered directly -- concrete subclasses (Eq, Ne, Gt, ...) register themselves.
    """

    # pylint: disable=redefined-builtin
    def __init__(self, input: PathOrCallable, value: Any = None, **dig_kwargs: Any) -> None:
        """Initialize a comparison condition.

        Args:
            input: A jmespath path/bare int shorthand/fallback list (extracted via
                Digger), or any callable/Op -- called directly against the item on
                every evaluation instead of going through Digger.
            value: The value to compare the extracted field against. Default: None.
            **dig_kwargs: Additional Digger/dig() kwargs (e.g. exp=, default=,
                converter=). Ignored when input= is a callable/Op.
        """
        self.input = input
        self.value = value
        self.dig_kwargs = dig_kwargs
        self._extract = input if callable(input) else Digger(path=input, **dig_kwargs)

    # pylint: enable=redefined-builtin

    def _extracted(self, item: Any) -> Any:
        return self._extract(item)

    def clone(self, **overrides: Any) -> "_Comparison":
        kwargs = {"input": self.input, "value": self.value, **self.dig_kwargs, **overrides}
        return type(self)(**kwargs)


@register("eq")
class Eq(_Comparison):
    """True when the extracted field equals value."""

    def __call__(self, item: Any) -> bool:
        return bool(self._extracted(item) == self.value)


@register("ne")
class Ne(_Comparison):
    """True when the extracted field does not equal value."""

    def __call__(self, item: Any) -> bool:
        return bool(self._extracted(item) != self.value)


@register("gt")
class Gt(_Comparison):
    """True when the extracted field is greater than value.

    A TypeError from comparing incompatible types (e.g. str vs int) is treated as
    False rather than raised -- one malformed record shouldn't crash a whole stream.
    """

    def __call__(self, item: Any) -> bool:
        try:
            return bool(self._extracted(item) > self.value)
        except TypeError:
            return False


@register("lt")
class Lt(_Comparison):
    """True when the extracted field is less than value. See Gt for the TypeError note."""

    def __call__(self, item: Any) -> bool:
        try:
            return bool(self._extracted(item) < self.value)
        except TypeError:
            return False


@register("ge")
class Ge(_Comparison):
    """True when the extracted field is >= value. See Gt for the TypeError note."""

    def __call__(self, item: Any) -> bool:
        try:
            return bool(self._extracted(item) >= self.value)
        except TypeError:
            return False


@register("le")
class Le(_Comparison):
    """True when the extracted field is <= value. See Gt for the TypeError note."""

    def __call__(self, item: Any) -> bool:
        try:
            return bool(self._extracted(item) <= self.value)
        except TypeError:
            return False


@register("in")
class In(_Comparison):
    """True when the extracted field is a member of value.

    A TypeError from an unhashable/uncontainable comparison is treated as False rather
    than raised. See Gt for the same rationale.
    """

    def __call__(self, item: Any) -> bool:
        try:
            return self._extracted(item) in self.value
        except TypeError:
            return False


@register("exists")
class Exists(_Comparison):
    """True when input resolves to a non-None value on the item."""

    # pylint: disable=redefined-builtin
    def __init__(self, input: PathOrCallable, **dig_kwargs: Any) -> None:
        super().__init__(input=input, value=None, **dig_kwargs)

    # pylint: enable=redefined-builtin

    def __call__(self, item: Any) -> bool:
        if callable(self.input):
            return self.input(item) is not None
        return dig(item, path=self.input, post_processor=None, **self.dig_kwargs) is not None

    def clone(self, **overrides: Any) -> "Exists":
        kwargs = {"input": self.input, **self.dig_kwargs, **overrides}
        return Exists(**kwargs)


@register("and")
class And(ItemOp):
    """True when every op in ops returns a truthy result for the item."""

    def __init__(self, ops: list[Op]) -> None:
        self.ops = ops

    def __call__(self, item: Any) -> bool:
        return all(op(item) for op in self.ops)


@register("or")
class Or(ItemOp):
    """True when any op in ops returns a truthy result for the item."""

    def __init__(self, ops: list[Op]) -> None:
        self.ops = ops

    def __call__(self, item: Any) -> bool:
        return any(op(item) for op in self.ops)


@register("xor")
class Xor(ItemOp):
    """Parity XOR across ops: True when an odd number of ops return a truthy result.

    This is the associative extension of Python's ^ operator to N operands, NOT "exactly
    one op is true" -- those two interpretations agree at N=2 but diverge beyond that
    (e.g. with 3 true operands, parity XOR is True; "exactly one" would be False).
    """

    def __init__(self, ops: list[Op]) -> None:
        self.ops = ops

    def __call__(self, item: Any) -> bool:
        return functools.reduce(operator.xor, (bool(op(item)) for op in self.ops), False)


@register("not")
class Not(ItemOp):
    """Negates a single condition op."""

    def __init__(self, op: Op) -> None:
        self.op = op

    def __call__(self, item: Any) -> bool:
        return not self.op(item)
