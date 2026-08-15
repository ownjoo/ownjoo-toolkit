# `oj_toolkit.ops` — a usage guide

Small, composable "op" classes that nest together to build a data-processing/logic
chain, and can equally be built from a plain JSON/YAML-shaped `dict` via `compile()`.
This guide is a tour for humans; the API reference lives in each module's docstrings
and in the top-level `README.md`'s `ops` section.

- [Mental model](#mental-model)
- [Item-level vs. stream-level, and why Map and Filter live apart](#item-level-vs-stream-level-and-why-map-and-filter-live-apart)
- [Quick start](#quick-start)
- [Op reference](#op-reference)
  - [Conditions (`conditions.py`)](#conditions-conditionspy)
  - [Control flow (`control.py`)](#control-flow-controlpy)
  - [Stream shaping (`iterate.py`)](#stream-shaping-iteratepy)
  - [Structure / fan-out-fan-in (`structure.py`)](#structure--fan-out-fan-in-structurepy)
  - [Whole-stream ops (`group.py`)](#whole-stream-ops-grouppy)
- [Going declarative: `register()` and `compile()`](#going-declarative-register-and-compile)
- [Recipes](#recipes)
- [Gotchas and design notes](#gotchas-and-design-notes)
- [Writing your own op](#writing-your-own-op)

## Mental model

Every op is a small class with a constructor and a `__call__`. There is no operator
overloading (no `a >> b`) -- composition is just nested constructor calls:

```python
Iter(fn=Map(fn=str.upper))
```

This is deliberate: nested constructors map 1:1 onto a declarative spec dict, so the
same chain can be written in Python or handed to you as JSON/YAML and `compile()`d at
runtime (see [Going declarative](#going-declarative-register-and-compile)). If you ever
reach for `>>`-style chaining, reach for nested constructors (or `Sequence`, below)
instead -- it's the one composition mechanism this package supports on purpose.

Every op subclasses `Op` (`oj_toolkit.ops.base.Op`), which gives you two things for
free on every op you build, including your own (see [Writing your own
op](#writing-your-own-op)):

- `describe()` / `repr()` -- a readable rendering of the op and its constructor args.
- `clone(**overrides)` -- rebuild an equivalent op, optionally swapping some
  constructor args.

## Item-level vs. stream-level, and why Map and Filter live apart

There are two "levels" of op, and the file layout follows this split rather than
alphabetical or "everything that sounds like a stream method" grouping:

- **Item-level ops** (`ItemOp`, `__call__(self, item) -> Any`) operate on a single
  object: one dict, one string, one number. Conditions (`And`, `Or`, `In`, `Eq`, ...),
  `When`, `Map`, `Sequence`, and the structure-reshaping ops (`Extract`, `Broadcast`,
  `Fanout`, `Merge`) are all item-level.
- **Stream-level ops** (`StreamOp`, `__call__(self, iterable) -> Iterator[Any]`)
  operate on a whole iterable, generator-in/generator-out. `Iter`, `Filter`, `FlatMap`,
  `GroupBy`, `Join`, `Zip` are stream-level.

`Iter` is the generic *lift* from item-level to stream-level -- analogous to how
Python's `map()` builtin actually bundles two separate ideas into one call: "the
function" and "the iteration machinery." Here those are split apart: `Map(fn)` is just
the function (item-level, lives in `control.py` next to `When`/`Sequence`), and
`Iter(fn=...)` is the iteration machinery (stream-level, lives in `iterate.py`).
`Iter(fn=Map(fn=str.upper))` together is what `map(str.upper, iterable)` does in one
step in plain Python.

**This is *why* `Map` and `Filter` don't sit next to each other despite looking like
siblings in most languages.** The two ops don't share a contract:

- `Map(fn)` is 1-item-in / 1-item-out. No cardinality change. That's exactly what makes
  it liftable by `Iter` -- a generic "apply this to each item" wrapper only works when
  applying it never changes how many items come out.
- `Filter(condition)` is 1-item-in / 0-or-1-item-out -- it can *drop* an item. That's a
  cardinality change, which `Iter`'s contract can't express. So `Filter` has to own its
  own stream loop; there's no item-level "filter" to lift, only the item-level
  *condition* it consumes (`In`, `Eq`, `And`, ... -- already item-level ops in their own
  right). `FlatMap` is the same story in the other direction: 1-in / 0-to-N-out.

So the real distinction isn't "Map and Filter are different in importance," it's "Map
doesn't change cardinality and Filter does" -- and that's what determines whether an op
needs `Iter` to run over a stream, or has to be stream-level on its own.

## Quick start

```python
from oj_toolkit.ops import Filter, In, Iter, Map

# map over a stream
list(Iter(fn=str.upper)(['a', 'b']))
# ['A', 'B']

# filter a stream of dicts by a condition
only_ok = Filter(condition=In(input='status', value=['ok', 'warn']))
list(only_ok([{'status': 'ok'}, {'status': 'fail'}]))
# [{'status': 'ok'}]

# item-level Map, lifted onto a stream with Iter
double = Iter(fn=Map(fn=lambda n: n * 2))
list(double([1, 2, 3]))
# [2, 4, 6]
```

## Op reference

Each op below is registered for `compile()` under the name shown in parentheses.

### Conditions (`conditions.py`)

All item-level, all return `bool`.

| Op | Signature | Notes |
|---|---|---|
| `Eq` (`'eq'`) | `Eq(input, value=None, **dig_kwargs)` | `extracted == value` |
| `Ne` (`'ne'`) | `Ne(input, value=None, **dig_kwargs)` | `extracted != value` |
| `Gt` / `Lt` / `Ge` / `Le` (`'gt'`/`'lt'`/`'ge'`/`'le'`) | same shape as `Eq` | comparison ops; a `TypeError` from comparing incompatible types (e.g. `str` vs `int`) is caught and treated as `False`, never raised |
| `In` (`'in'`) | `In(input, value=None, **dig_kwargs)` | `extracted in value`; a `TypeError` (e.g. `value` isn't a container) is also caught and treated as `False` |
| `Exists` (`'exists'`) | `Exists(input, **dig_kwargs)` | `True` when `input` resolves to a non-`None` value |
| `And` (`'and'`) | `And(ops)` | `all(op(item) for op in ops)` |
| `Or` (`'or'`) | `Or(ops)` | `any(op(item) for op in ops)` |
| `Xor` (`'xor'`) | `Xor(ops)` | **parity** XOR -- see [Gotchas](#gotchas-and-design-notes) |
| `Not` (`'not'`) | `Not(op)` | negates a single op |

`input=` is a [jmespath](https://jmespath.org/) path (or a bare `int` shorthand, or a
`list` of fallback paths), extracted via `oj_toolkit.parsing.Digger` -- exactly the same
path syntax as `dig()`/`Digger` elsewhere in this library. `**dig_kwargs` forwards
straight through (`exp=`, `default=`, `converter=`, `pattern=`, etc.).

```python
from oj_toolkit.ops import And, Eq, In, Not

is_healthy = And(ops=[
    In(input='status', value=['ok', 'warn']),
    Not(op=Eq(input='region', value='deprecated')),
])
is_healthy({'status': 'ok', 'region': 'us-east'})   # True
is_healthy({'status': 'fail', 'region': 'us-east'}) # False
```

### Control flow (`control.py`)

Item-level.

| Op | Signature | Notes |
|---|---|---|
| `When` (`'when'`) | `When(condition, then, otherwise=None)` | branches between two item-level ops; see default-`otherwise` behavior below |
| `Map` (`'map'`) | `Map(fn)` | applies any plain callable to the item -- `fn` need not be an `Op` |
| `Sequence` (`'sequence'`) | `Sequence(ops)` | threads the item through a flat list of item-level ops in order |

```python
from oj_toolkit.ops import Eq, Map, Sequence, When

tag_prod = When(
    condition=Eq(input='env', value='prod'),
    then=Map(fn=lambda item: {**item, 'critical': True}),
    # no otherwise= -> item passes through unchanged when condition is False
)
tag_prod({'env': 'prod'})  # {'env': 'prod', 'critical': True}
tag_prod({'env': 'dev'})   # {'env': 'dev'} -- unchanged

clean = Sequence(ops=[
    Map(fn=str.strip),
    Map(fn=str.lower),
    Map(fn=lambda s: s.replace(' ', '_')),
])
clean('  Hello World  ')  # 'hello_world'
```

`Sequence` is the flat, linear escape hatch for chains that would otherwise nest
inside-out and become hard to read (`A(B(C(x)))`) -- reach for it once a chain grows
past two or three steps.

### Stream shaping (`iterate.py`)

Stream-level: `Iterable -> Iterator`.

| Op | Signature | Notes |
|---|---|---|
| `Iter` (`'iter'`) | `Iter(fn)` | lifts a single-item callable (`fn`) to run over a stream, 1-in/1-out |
| `Filter` (`'filter'`) | `Filter(condition)` | keeps only items where `condition(item)` is truthy |
| `FlatMap` (`'flat_map'`) | `FlatMap(op)` | applies `op` to each item, expects an iterable result, and flattens it into the output stream |

`fn` is required, with no default -- `Iter()` (or a `{"type": "iter"}` spec with no
`fn` key) raises `TypeError` immediately at construction, not deferred to the first
call. `Iter(fn=42)` -- any non-callable value -- fails the same way, at construction.

```python
from oj_toolkit.ops import FlatMap, Iter, Map

list(Iter(fn=str.upper)(['a', 'b']))
# ['A', 'B']

# one item expands into many
list(FlatMap(op=Map(fn=lambda n: [n, n]))([1, 2]))
# [1, 1, 2, 2]
```

### Structure / fan-out-fan-in (`structure.py`)

Item-level; reshape a single record.

| Op | Signature | Notes |
|---|---|---|
| `Extract` (`'extract'`) | `Extract(path, **dig_kwargs)` | thin wrapper around `Digger` -- pulls one field out of an item |
| `Broadcast` (`'broadcast'`) | `Broadcast(children_path, fields, **dig_kwargs)` | combines selected parent fields with each of the parent's child records; returns a `list[dict]` |
| `Fanout` (`'fanout'`) | `Fanout(**ops)` | runs several *named* item-level ops against the same item, collects results into a `dict` |
| `Merge` (`'merge'`) | `Merge(ops)` | runs several *dict-producing* item-level ops against the same item and shallow-merges the results (later overwrites earlier) |

```python
from oj_toolkit.ops import Extract, Fanout, In

summarize = Fanout(
    status=Extract(path='status'),
    is_ok=In(input='status', value=['ok', 'warn']),
)
summarize({'status': 'ok', 'noise': 'ignored'})
# {'status': 'ok', 'is_ok': True}
```

`Fanout`'s constructor takes `**ops` on purpose: a spec dict
`{"type": "fanout", "status": {...}, "is_ok": {...}}` maps directly onto
`Fanout(status=..., is_ok=...)` with zero special-casing in `compile()` -- every
non-`"type"` key in a spec already becomes a keyword argument.

`Broadcast` is the "compute enclosure with blades" op -- combining a few parent fields
with a list of child records nested inside the parent. It returns a `list`, so pair it
with `FlatMap` to expand a stream of parents into a stream of parent+child records (see
[Recipes](#recipes) below).

### Whole-stream ops (`group.py`)

Stream-level; these either need to see the entire input before producing output, or
combine multiple streams.

| Op | Signature | Notes |
|---|---|---|
| `GroupBy` (`'group_by'`) | `GroupBy(key)` | groups the whole stream into `dict[key, list[item]]`; **eager**, returns a `dict`, not a generator (see [Gotchas](#gotchas-and-design-notes)) |
| `Join` (`'join'`) | `Join(right, on, right_on=None, how='inner')` | joins the stream against an already-materialized `list` on an equality key; v1 scope only (see [Gotchas](#gotchas-and-design-notes)) |
| `Zip` (`'zip'`) | `Zip(others, strict=False)` | thin wrapper around `zip()` |

`key=` on `GroupBy` accepts either a jmespath path (`str`) or any callable
(`item -> Any`), including another op.

```python
from oj_toolkit.ops import GroupBy, Join

records = [{'team': 'a', 'n': 1}, {'team': 'b', 'n': 2}, {'team': 'a', 'n': 3}]
GroupBy(key='team')(records)
# {'a': [{'team': 'a', 'n': 1}, {'team': 'a', 'n': 3}], 'b': [{'team': 'b', 'n': 2}]}

teams = [{'team_id': 'a', 'name': 'Alpha'}, {'team_id': 'b', 'name': 'Beta'}]
enrich = Join(right=teams, on='team', right_on='team_id')
list(enrich(records))
# [{'team': 'a', 'n': 1, 'team_id': 'a', 'name': 'Alpha'},
#  {'team': 'b', 'n': 2, 'team_id': 'b', 'name': 'Beta'},
#  {'team': 'a', 'n': 3, 'team_id': 'a', 'name': 'Alpha'}]
```

## Going declarative: `register()` and `compile()`

Every op above is registered under a short string name (shown in parentheses in the
tables above). `compile()` turns a plain `dict`/`list`-shaped spec into the equivalent
tree of op instances:

- A `dict` (technically any `Mapping`) containing a `"type"` key is compiled into an
  `Op`: every *other* key's value is itself recursively compiled, then the registered
  class is instantiated as `cls(**resolved_kwargs)`.
- A `list` has each element recursively compiled.
- Anything else -- including a `dict` **without** a `"type"` key, like `Fanout`'s
  per-field mapping or a `dig_many()`-style `paths=` dict -- is returned unchanged.
  This is what lets `Fanout`'s arbitrary field names and jmespath path strings pass
  through untouched.

```python
from oj_toolkit.ops import compile as compile_ops

spec = {
    'type': 'filter',
    'condition': {
        'type': 'and',
        'ops': [
            {'type': 'in', 'input': 'status', 'value': ['ok', 'warn']},
            {'type': 'not', 'op': {'type': 'eq', 'input': 'region', 'value': 'deprecated'}},
        ],
    },
}
op = compile_ops(spec)
list(op([
    {'status': 'ok', 'region': 'us-east'},
    {'status': 'ok', 'region': 'deprecated'},
    {'status': 'fail', 'region': 'us-east'},
]))
# [{'status': 'ok', 'region': 'us-east'}]
```

`compile` shadows the `compile()` builtin on purpose -- import it aliased so it doesn't
shadow the builtin in *your* module's scope:

```python
from oj_toolkit.ops import compile as compile_ops
# or, from the top-level package:
from oj_toolkit import compile_ops, register_op
```

Spec dicts aren't required to be JSON-serializable -- values like `Map`'s `fn=` can be
real Python callables embedded directly in the dict, not just JSON literals. If you
need specs to round-trip through actual JSON/YAML text, keep `fn=` out of them (use
`Sequence`/conditions/structure ops instead, or resolve function names to callables
yourself before calling `compile()`).

## Recipes

**Fan out a parent record's children ("enclosure with blades"):**

```python
from oj_toolkit.ops import Broadcast, FlatMap

expand_blades = FlatMap(op=Broadcast(
    children_path='blades',
    fields={'enclosure_id': 'enclosure_id', 'location': 'location'},
))
list(expand_blades([{
    'enclosure_id': 'abc', 'location': 'rack1',
    'blades': [{'serial': 'b1'}, {'serial': 'b2'}],
}]))
# [{'enclosure_id': 'abc', 'location': 'rack1', 'serial': 'b1'},
#  {'enclosure_id': 'abc', 'location': 'rack1', 'serial': 'b2'}]
```

**Conditionally tag records flowing through a stream:**

```python
from oj_toolkit.ops import And, Eq, Gt, Iter, Map, When

flag_hot_prod = Iter(fn=When(
    condition=And(ops=[Gt(input='cpu', value=80), Eq(input='env', value='prod')]),
    then=Map(fn=lambda item: {**item, 'alert': True}),
))
list(flag_hot_prod([
    {'cpu': 90, 'env': 'prod'},
    {'cpu': 50, 'env': 'prod'},
]))
# [{'cpu': 90, 'env': 'prod', 'alert': True}, {'cpu': 50, 'env': 'prod'}]
```

**Build a summary record with `Fanout`, then filter the stream on it:**

```python
from oj_toolkit.ops import Eq, Extract, Fanout, Filter, Iter

summarize = Iter(fn=Fanout(
    id=Extract(path='id'),
    healthy=Eq(input='status', value='ok'),
))
only_healthy = Filter(condition=Eq(input='healthy', value=True))

records = [{'id': 1, 'status': 'ok'}, {'id': 2, 'status': 'fail'}]
list(only_healthy(summarize(records)))
# [{'id': 1, 'healthy': True}]
```

> For chaining a stream-level op's *output* into another stream-level op, just call
> them in sequence in Python (`only_healthy(summarize(records))`) -- `Sequence` is for
> item-level chains, not stream-level ones. There's no dedicated stream-level
> "sequence" op in v1; ordinary function composition already does the job cleanly
> since every `StreamOp` is `Iterable -> Iterator`.

## Gotchas and design notes

- **`Xor` is parity XOR, not "exactly one true."** `Xor(ops=[a, b, c])` is `True` when
  an *odd* number of operands are truthy -- the associative extension of Python's `^`
  to N operands. With 2 operands this matches "exactly one true," but with 3 it
  doesn't: three truthy operands is `True` under parity XOR, `False` under "exactly
  one."
- **`When` with no `otherwise=` passes the item through unchanged**, not `None`. This
  is the least surprising default for a data pipeline ("if X, do Y; otherwise leave it
  alone") but it does mean a missing `otherwise=` is not the same as
  `otherwise=Map(fn=lambda item: None)`.
- **Comparison conditions swallow `TypeError`, not other exceptions.** `Gt`, `Lt`,
  `Ge`, `Le`, and `In` catch a `TypeError` from an incompatible comparison (e.g.
  comparing a `str` field to an `int` value) and return `False` rather than raising --
  one malformed record shouldn't crash a whole stream. Other exception types are not
  caught.
- **`GroupBy` returns a `dict`, not a generator**, and is the one documented exception
  among `StreamOp`s. Grouping fundamentally requires seeing every item before any
  group is "done," so pretending it's lazy would be dishonest -- it consumes its whole
  input eagerly, in one pass.
- **`Join` is intentionally minimal in v1**: a single equality key, `'inner'` or
  `'left'` only, and `right` must already be a materialized `list` (not a stream). A
  key collision between a left and right record resolves in the right record's favor.
  Multi-key joins, `'outer'`, and a streamed right side are not implemented.
- **`Iter` validates `fn` at construction, not at first call.** `fn` has no default --
  `Iter()` and `Iter(fn=<non-callable>)` both raise `TypeError` immediately, so a bare
  `{"type": "iter"}` spec fails inside `compile()` itself rather than succeeding and
  breaking later on first use.
- **`compile` and `register` shadow builtins.** Import them aliased:
  `from oj_toolkit.ops import compile as compile_ops`. The top-level package already
  re-exports them pre-aliased as `oj_toolkit.compile_ops` / `oj_toolkit.register_op`.

## Writing your own op

```python
from oj_toolkit.ops import ItemOp, register

@register('shout')
class Shout(ItemOp):
    def __init__(self, suffix: str = '!') -> None:
        self.suffix = suffix

    def __call__(self, item):
        return f'{item.upper()}{self.suffix}'
```

That's the whole contract: subclass `ItemOp` or `StreamOp`, store constructor
parameters as same-named instance attributes (so the inherited `describe()`/`clone()`
work without any extra code), implement `__call__`, and register it under a name if
you want it reachable from `compile()`. Once registered, it composes with every
built-in op exactly the same way:

```python
from oj_toolkit.ops import compile as compile_ops

op = compile_ops({'type': 'iter', 'fn': {'type': 'shout', 'suffix': '!!'}})
list(op(['hi', 'there']))
# ['HI!!', 'THERE!!']
```

If your constructor uses `**kwargs` (catch-all keyword args) rather than one
same-named attribute per parameter, override `clone()` yourself -- see
`_Comparison.clone()` in `conditions.py`, `Extract.clone()` / `Broadcast.clone()` /
`Fanout.clone()` in `structure.py` for the pattern.
