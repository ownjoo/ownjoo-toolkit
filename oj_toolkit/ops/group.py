"""Stream-level ops that need to see the whole stream at once, or combine multiple
streams: GroupBy, Join, Zip.
"""

from collections.abc import Iterable, Iterator, Mapping
from typing import Any

from oj_toolkit.ops.base import Op, StreamOp
from oj_toolkit.ops.registry import register
from oj_toolkit.parsing import Digger, dig

_JOIN_HOW_VALUES = ("inner", "left")


def _join_key(row: Mapping, spec: str | list[str]) -> Any:
    """Extract Join's equality key from row: a single dig() value for a str spec, or a
    tuple of dig() values (composite key) for a list[str] spec.
    """
    if isinstance(spec, list):
        return tuple(dig(row, path=path) for path in spec)
    return dig(row, path=spec)


@register("group_by")
class GroupBy(StreamOp):
    """Group a stream into a dict[key, list[item]].

    Eager and single-pass -- grouping must consume the whole input before any group is
    complete, so this deliberately returns a dict rather than a generator; it's the one
    documented exception among StreamOps.

    Attributes:
        key: A jmespath path (via Digger) or a callable(item) -> Any used to compute each
            item's group key.
    """

    def __init__(self, key: str | Op) -> None:
        self.key = key
        self._key_fn = key if callable(key) else Digger(path=key)

    def __call__(self, i: Iterable[Any]) -> dict[Any, list[Any]]:
        groups: dict[Any, list[Any]] = {}
        for item in i:
            groups.setdefault(self._key_fn(item), []).append(item)
        return groups


@register("join")
class Join(StreamOp):
    """Join a stream of left records against an already-materialized list of right
    records on an equality key.

    v1 scope: 'inner' or 'left' only, right must already be a materialized list (not a
    stream). One-to-many matches are supported (each matching right row yields a
    separate output record); on key collision between a left and right record, the
    right record's fields win.

    Attributes:
        right: The already-materialized list of records to join against.
        on: The jmespath path identifying the join key on left (input) records, or a
            list of paths for a composite (multi-field) equality key.
        right_on: The jmespath path (or list of paths) identifying the join key on
            right records. Default: None, meaning the same path(s) as on.
        how: 'inner' (drop left records with no match) or 'left' (keep them, unmerged).
            Default: 'inner'.
    """

    def __init__(
        self,
        right: list[Mapping],
        on: str | list[str],
        right_on: str | list[str] | None = None,
        how: str = "inner",
    ) -> None:
        if how not in _JOIN_HOW_VALUES:
            raise ValueError(f"how must be one of {_JOIN_HOW_VALUES}, got {how!r}")
        self.right = right
        self.on = on
        self.right_on = right_on
        self.how = how
        right_key_spec = right_on or on
        index: dict[Any, list[Mapping]] = {}
        for row in right:
            index.setdefault(_join_key(row, right_key_spec), []).append(row)
        self._index = index

    def __call__(self, i: Iterable[Mapping]) -> Iterator[dict]:
        for left_item in i:
            matches = self._index.get(_join_key(left_item, self.on))
            if matches:
                for right_item in matches:
                    yield {**left_item, **right_item}
            elif self.how == "left":
                yield dict(left_item)


@register("zip")
class Zip(StreamOp):
    """Zip a stream together with one or more other already-materialized iterables.

    A thin wrapper around the zip() builtin.

    Attributes:
        others: Additional iterables to zip alongside the input stream.
        strict: If True, raise ValueError when the iterables have mismatched lengths
            (same semantics as zip(..., strict=True)). Default: False.
    """

    def __init__(self, others: list[Iterable[Any]], strict: bool = False) -> None:
        self.others = others
        self.strict = strict

    def __call__(self, i: Iterable[Any]) -> Iterator[tuple]:
        yield from zip(i, *self.others, strict=self.strict)
