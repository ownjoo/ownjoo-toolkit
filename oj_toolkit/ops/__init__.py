"""Composable, nestable "op" classes for building data-processing/logic chains, plus a
registry and compile() function for building the same chains declaratively from a
JSON/YAML spec dict.

Two op "levels":
- Item-level ops (__call__(self, item) -> Any): conditions (And, Or, Xor, Not, In, Eq,
  Ne, Gt, Lt, Ge, Le, Exists), control flow (When, Map, Sequence), structure
  manipulation (Extract, Resolve, MapField, Broadcast, Fanout, Merge), key/value
  reshaping (Pick, Omit, Rename, SetField), and time (Now, Elapsed).
- Stream-level ops (__call__(self, iterable) -> Iterator[Any]): Iter (the generic lift of
  any single-item callable), Filter, FlatMap, GroupBy, Join, Zip, and Pipeline (chains
  other StreamOps in sequence -- the stream-level counterpart to Sequence).

Composition is plain nested constructor calls -- no operator overloading -- which maps
1:1 onto a declarative spec: Iter(Map(str.upper)) <-> {"type": "iter", "fn":
{"type": "map", "fn": str.upper}}.

Every comparison's input= (and Elapsed's since=) accepts either a jmespath path
(extracted via Digger) or any callable/Op, evaluated fresh against the item on every
call -- this is what lets Elapsed/Resolve/Now plug into And/Or/Gt/etc. like any other
value source: Gt(input=Elapsed(since='created_at'), value=300).

Glom is an escape hatch to the third-party glom library's spec language, for cases
dig()/resolve() can't express (e.g. calling a method with real arguments partway
through a path). It's an optional dependency -- importing oj_toolkit.ops never
requires glom, only constructing a Glom instance does. Install it with:
pip install 'oj-toolkit[glom]'
"""

from oj_toolkit.ops.base import ItemOp, Op, StreamOp
from oj_toolkit.ops.clock import Elapsed, Now
from oj_toolkit.ops.conditions import And, Eq, Exists, Ge, Gt, In, Le, Lt, Ne, Not, Or, Xor
from oj_toolkit.ops.control import Map, Sequence, When
from oj_toolkit.ops.glom_op import Glom
from oj_toolkit.ops.group import GroupBy, Join, Zip
from oj_toolkit.ops.iterate import Filter, FlatMap, Iter
from oj_toolkit.ops.keys import Omit, Pick, Rename, SetField
from oj_toolkit.ops.pipeline import Pipeline
from oj_toolkit.ops.registry import compile, register  # pylint: disable=redefined-builtin
from oj_toolkit.ops.structure import Broadcast, Extract, Fanout, MapField, Merge, Resolve

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
    "Resolve",
    "Glom",
    "MapField",
    "Broadcast",
    "Fanout",
    "Merge",
    "Pick",
    "Omit",
    "Rename",
    "SetField",
    "Now",
    "Elapsed",
    "GroupBy",
    "Join",
    "Zip",
    "Pipeline",
]
