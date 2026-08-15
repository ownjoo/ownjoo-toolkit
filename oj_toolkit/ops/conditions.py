"""Boolean condition ops: comparisons against an extracted field, and logic combinators.

Every comparison op extracts a value from the item via dig()/Digger (see
oj_toolkit.parsing.types) using an input= jmespath path, then compares it to value=.
"""

import functools
import operator
from typing import Any

from oj_toolkit.ops.base import ItemOp, Op
from oj_toolkit.ops.registry import register
from oj_toolkit.parsing import Digger, dig


class _Comparison(ItemOp):  # pylint: disable=abstract-method
    """Shared base for ops that extract a field via dig()/Digger and compare it to value.

    Not registered directly -- concrete subclasses (Eq, Ne, Gt, ...) register themselves.
    """

    # pylint: disable-next=redefined-builtin
    def __init__(self, input: str, value: Any = None, **dig_kwargs: Any) -> None:
        """Initialize a comparison condition.

        Args:
            input: A jmespath path (or bare int shorthand) identifying the field to
                extract from the item. Passed straight to Digger.
            value: The value to compare the extracted field against. Default: None.
            **dig_kwargs: Additional Digger/dig() kwargs (e.g. exp=, default=, converter=).
        """
        self.input = input
        self.value = value
        self.dig_kwargs = dig_kwargs
        self._digger = Digger(path=input, **dig_kwargs)

    def _extracted(self, item: Any) -> Any:
        return self._digger(item)

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

    # pylint: disable-next=redefined-builtin
    def __init__(self, input: str, **dig_kwargs: Any) -> None:
        super().__init__(input=input, value=None, **dig_kwargs)

    def __call__(self, item: Any) -> bool:
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
