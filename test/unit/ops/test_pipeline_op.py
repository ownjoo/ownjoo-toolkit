"""Tests for Pipeline."""

import unittest

from oj_toolkit.ops.conditions import Eq
from oj_toolkit.ops.control import Map
from oj_toolkit.ops.iterate import Filter, Iter
from oj_toolkit.ops.pipeline import Pipeline
from oj_toolkit.ops.registry import compile  # pylint: disable=redefined-builtin


class TestPipeline(unittest.TestCase):
    """Tests for Pipeline."""

    def test_should_chain_stream_ops_in_order(self):
        # setup
        expected = [{'status': 'ok', 'seen': True}]
        pipeline = Pipeline(
            ops=[
                Filter(condition=Eq(input='status', value='ok')),
                Iter(fn=Map(fn=lambda item: {**item, 'seen': True})),
            ]
        )

        # execute
        actual = list(pipeline([{'status': 'ok'}, {'status': 'fail'}]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_pass_through_unchanged_for_empty_ops_list(self):
        # setup
        expected = [1, 2, 3]
        pipeline = Pipeline(ops=[])

        # execute
        actual = list(pipeline([1, 2, 3]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_be_lazy_not_materialize_intermediate_stages(self):
        # setup
        seen = []

        def track(item):
            seen.append(item)
            return item

        pipeline = Pipeline(ops=[Iter(fn=track)])

        # execute -- constructing and calling the pipeline shouldn't consume anything
        result = pipeline([1, 2, 3])

        # assess
        self.assertEqual([], seen)
        next(result)
        self.assertEqual([1], seen)

        # teardown

    def test_should_compose_with_compile(self):
        # setup
        expected = [{'status': 'ok', 'seen': True}]
        spec = {
            'type': 'pipeline',
            'ops': [
                {'type': 'filter', 'condition': {'type': 'eq', 'input': 'status', 'value': 'ok'}},
                {'type': 'iter', 'fn': {'type': 'map', 'fn': lambda item: {**item, 'seen': True}}},
            ],
        }
        op = compile(spec)

        # execute
        actual = list(op([{'status': 'ok'}, {'status': 'fail'}]))

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
