"""Base classes for the ops package.

Every op is a small callable class. Subclasses store each constructor parameter as a
same-named public instance attribute -- describe() and clone() below rely on that
convention, the same way FlexMixin.to_dict() relies on vars(self).
"""

from typing import Any, ClassVar


class Op:
    """Base class for all ops.

    Subclasses implement __call__. Two "levels" exist (see ItemOp and StreamOp below);
    Op itself carries no assumption about which.

    Attributes:
        type_name: The name this class is registered under via @register(), or None if
            it isn't registered for declarative compile().
    """

    type_name: ClassVar[str | None] = None

    def __call__(self, arg: Any) -> Any:
        raise NotImplementedError

    def describe(self) -> str:
        """Render this op and its constructor parameters as a readable string."""
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items() if not k.startswith("_"))
        return f"{type(self).__name__}({attrs})"

    def clone(self, **overrides: Any) -> "Op":
        """Build a new instance of this op, reusing its constructor parameters.

        Args:
            **overrides: Constructor parameters to replace on the clone.

        Returns:
            A new instance of type(self), built from this op's stored parameters with
            overrides applied on top.
        """
        kwargs = {k: v for k, v in vars(self).items() if not k.startswith("_")}
        kwargs.update(overrides)
        return type(self)(**kwargs)

    def __repr__(self) -> str:
        return self.describe()


class ItemOp(Op):  # pylint: disable=abstract-method
    """An op that operates on a single item: __call__(self, item) -> Any."""


class StreamOp(Op):  # pylint: disable=abstract-method
    """An op that operates on a whole iterable, generator-in/generator-out:
    __call__(self, iterable) -> Iterator[Any].

    GroupBy is the one documented exception -- see group.py.
    """
