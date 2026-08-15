"""Composable, nestable "op" classes for building data-processing/logic chains, plus a
registry and compile() function for building the same chains declaratively from a
JSON/YAML spec dict.

Two op "levels":
- Item-level ops (__call__(self, item) -> Any): conditions (And, Or, Xor, Not, In, Eq,
  Ne, Gt, Lt, Ge, Le, Exists), control flow (When, Map, Sequence), and structure
  manipulation (Extract, Broadcast, Fanout, Merge).
- Stream-level ops (__call__(self, iterable) -> Iterator[Any]): Iter (the generic lift of
  any single-item callable), Filter, FlatMap, GroupBy, Join, Zip.

Composition is plain nested constructor calls -- no operator overloading -- which maps
1:1 onto a declarative spec: Iter(Map(str.upper)) <-> {"type": "iter", "fn":
{"type": "map", "fn": str.upper}}.
"""

from oj_toolkit.ops.base import ItemOp, Op, StreamOp
from oj_toolkit.ops.conditions import And, Eq, Exists, Ge, Gt, In, Le, Lt, Ne, Not, Or, Xor
from oj_toolkit.ops.control import Map, Sequence, When
from oj_toolkit.ops.group import GroupBy, Join, Zip
from oj_toolkit.ops.iterate import Filter, FlatMap, Iter
from oj_toolkit.ops.registry import compile, register  # pylint: disable=redefined-builtin
from oj_toolkit.ops.structure import Broadcast, Extract, Fanout, Merge

__all__ = [
    "Op",
    "ItemOp",
    "StreamOp",
    "register",
    "compile",
    "And",
    "Or",
    "Xor",
    "Not",
    "In",
    "Eq",
    "Ne",
    "Gt",
    "Lt",
    "Ge",
    "Le",
    "Exists",
    "When",
    "Map",
    "Sequence",
    "Iter",
    "Filter",
    "FlatMap",
    "Extract",
    "Broadcast",
    "Fanout",
    "Merge",
    "GroupBy",
    "Join",
    "Zip",
]
