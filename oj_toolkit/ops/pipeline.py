"""Pipeline: the stream-level counterpart to Sequence.

Sequence (control.py) threads an item through a flat list of item-level ops. Pipeline
does the same thing one level up: threads an iterable through a flat list of
StreamOps, each stage's output feeding the next stage's input. Lazy -- it doesn't
materialize the stream at any stage; it just chains the generators.

Before Pipeline, chaining StreamOps meant writing it as nested/sequential Python calls
(op2(op1(stream))) -- that works, but it can't be produced by compile() from a spec,
since nothing let one StreamOp name "the next stage to run." Pipeline closes that gap.
"""

from collections.abc import Iterable, Iterator
from typing import Any

from oj_toolkit.ops.base import StreamOp
from oj_toolkit.ops.registry import register


@register("pipeline")
class Pipeline(StreamOp):
    """Chain StreamOps in sequence, passing each stage's output as the next stage's input."""

    def __init__(self, ops: list[StreamOp]) -> None:
        self.ops = ops

    def __call__(self, iterable: Iterable[Any]) -> Iterator[Any]:
        stream: Iterable[Any] = iterable
        for op in self.ops:
            stream = op(stream)
        return iter(stream)
