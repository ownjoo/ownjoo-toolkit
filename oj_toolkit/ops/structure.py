"""Item-level fan-out/fan-in ops for reshaping a single record: Extract, Resolve,
MapField, Broadcast, Fanout, Merge.
"""

from collections.abc import Mapping
from typing import Any, Callable

from oj_toolkit.ops.base import ItemOp, Op
from oj_toolkit.ops.registry import register
from oj_toolkit.parsing import Digger, dig, dig_many, resolve


@register("extract")
class Extract(ItemOp):
    """Pull a single field out of an item via dig()/Digger.

    A thin wrapper -- all path navigation, type checking, and default handling is
    delegated straight to Digger.
    """

    def __init__(self, path: int | str | list[int | str] | None = None, **dig_kwargs: Any) -> None:
        self.path = path
        self.dig_kwargs = dig_kwargs
        self._digger = Digger(path=path, **dig_kwargs)

    def __call__(self, item: Any) -> Any:
        return self._digger(item)

    def clone(self, **overrides: Any) -> "Extract":
        kwargs = {"path": self.path, **self.dig_kwargs, **overrides}
        return Extract(**kwargs)


@register("resolve")
class Resolve(ItemOp):
    """Navigate an arbitrary Python object -- not just dicts/lists -- via
    oj_toolkit.parsing.resolve(): attribute/method access, auto-calling anything
    callable found along the path. Extract's counterpart for non-dict/list items, e.g.
    an httpx.Response's .status_code, .headers, or .json().
    """

    def __init__(self, path: str, default: Any = None, sep: str = ".") -> None:
        self.path = path
        self.default = default
        self.sep = sep

    def __call__(self, item: Any) -> Any:
        return resolve(item, path=self.path, default=self.default, sep=self.sep)


@register("map_field")
class MapField(ItemOp):
    """Apply fn to one field of a dict item, leaving the rest of the item unchanged.

    The read side goes through Digger (so exp=/default=/etc. from dig_kwargs still
    apply to the value fn receives). The write side is always a shallow item[key] = ...
    on a copy of item -- v1 scope: key is a flat top-level dict key, not a full
    jmespath path; general nested-path write-back isn't implemented.
    """

    def __init__(self, key: str, fn: Callable[[Any], Any], **dig_kwargs: Any) -> None:
        self.key = key
        self.fn = fn
        self.dig_kwargs = dig_kwargs
        self._digger = Digger(path=key, **dig_kwargs)

    def __call__(self, item: Mapping) -> dict:
        return {**item, self.key: self.fn(self._digger(item))}

    def clone(self, **overrides: Any) -> "MapField":
        kwargs = {"key": self.key, "fn": self.fn, **self.dig_kwargs, **overrides}
        return MapField(**kwargs)


@register("broadcast")
class Broadcast(ItemOp):
    """Combine selected parent fields with each of the parent's child records.

    The "compute enclosure with blades" case: given a parent dict containing a list of
    child dicts, produce one merged record per child, each carrying the requested parent
    fields alongside the child's own fields. Used together with FlatMap when processing a
    stream of parents (see iterate.py).

    Attributes:
        children_path: A jmespath path (via dig()) locating the list of child records on
            the parent item.
        fields: Maps an output key to a jmespath path (via dig_many()) identifying a
            parent field to copy into every child record.
    """

    def __init__(
        self,
        children_path: int | str | list[int | str],
        fields: Mapping[str, Any],
        **dig_kwargs: Any,
    ) -> None:
        self.children_path = children_path
        self.fields = fields
        self.dig_kwargs = dig_kwargs

    def __call__(self, item: Any) -> list[dict]:
        parent_values = dig_many(item, paths=self.fields)
        children = dig(item, path=self.children_path, exp=list, default=[], **self.dig_kwargs)
        return [{**parent_values, **child} for child in children]

    def clone(self, **overrides: Any) -> "Broadcast":
        kwargs = {
            "children_path": self.children_path,
            "fields": self.fields,
            **self.dig_kwargs,
            **overrides,
        }
        return Broadcast(**kwargs)


@register("fanout")
class Fanout(ItemOp):
    """Run several named item-level ops against the same item, collecting results into a
    dict keyed by the kwarg names.

    A spec like {"type": "fanout", "status": {...}, "is_ok": {...}} maps directly onto
    Fanout(status=..., is_ok=...) -- compile() needs no special-casing for this, since
    every non-"type" key already becomes a kwarg.
    """

    def __init__(self, **ops: Op) -> None:
        self.ops = ops

    def __call__(self, item: Any) -> dict[str, Any]:
        return {name: op(item) for name, op in self.ops.items()}

    def clone(self, **overrides: Any) -> "Fanout":
        return Fanout(**{**self.ops, **overrides})


@register("merge")
class Merge(ItemOp):
    """Run several dict-producing item-level ops against the same item and shallow-merge
    their results into one dict. Later ops overwrite earlier ops on key collision.
    """

    def __init__(self, ops: list[Op]) -> None:
        self.ops = ops

    def __call__(self, item: Any) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for op in self.ops:
            result.update(op(item))
        return result
