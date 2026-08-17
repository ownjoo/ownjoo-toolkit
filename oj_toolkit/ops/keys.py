"""Item-level ops that reshape a dict item by key: Pick, Omit, Rename, SetField."""

from collections.abc import Mapping
from typing import Any

from oj_toolkit.ops.base import ItemOp
from oj_toolkit.ops.registry import register


@register("pick")
class Pick(ItemOp):
    """Keep only the given keys from a dict item; drop everything else.

    Missing keys are silently skipped rather than raising -- a partial record still
    produces a (smaller) result. Output key order follows keys, not item.
    """

    def __init__(self, keys: list[str]) -> None:
        self.keys = keys

    def __call__(self, item: Mapping) -> dict:
        return {k: item[k] for k in self.keys if k in item}


@register("omit")
class Omit(ItemOp):
    """Drop the given keys from a dict item; keep everything else."""

    def __init__(self, keys: list[str]) -> None:
        self.keys = keys

    def __call__(self, item: Mapping) -> dict:
        return {k: v for k, v in item.items() if k not in self.keys}


@register("rename")
class Rename(ItemOp):
    """Rename dict keys per a mapping ({old_key: new_key}); keys not listed in mapping
    pass through under their original name unchanged.
    """

    def __init__(self, mapping: Mapping[str, str]) -> None:
        self.mapping = mapping

    def __call__(self, item: Mapping) -> dict:
        return {self.mapping.get(k, k): v for k, v in item.items()}


@register("set_field")
class SetField(ItemOp):
    """Set a dict item's key to a literal constant value, leaving the rest of the item
    unchanged. MapField's counterpart for "always this value" instead of "transform the
    existing value."
    """

    def __init__(self, key: str, value: Any) -> None:
        self.key = key
        self.value = value

    def __call__(self, item: Mapping) -> dict:
        return {**item, self.key: self.value}
