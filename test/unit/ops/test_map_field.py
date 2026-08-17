"""Tests for MapField."""

import unittest

from oj_toolkit.ops.control import Map, Sequence
from oj_toolkit.ops.structure import MapField


class TestMapField(unittest.TestCase):
    """Tests for MapField."""

    def test_should_transform_only_the_named_field(self):
        # setup
        expected = {'status': 'OK', 'other': 'unchanged'}
        op = MapField(key='status', fn=str.upper)

        # execute
        actual = op({'status': 'ok', 'other': 'unchanged'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_not_mutate_the_original_item(self):
        # setup
        original = {'status': 'ok'}
        op = MapField(key='status', fn=str.upper)

        # execute
        op(original)

        # assess
        self.assertEqual('ok', original['status'])

        # teardown

    def test_should_compose_fn_from_a_sequence(self):
        # setup
        expected = {'status': 'ok'}
        op = MapField(key='status', fn=Sequence(ops=[Map(fn=str.strip), Map(fn=str.lower)]))

        # execute
        actual = op({'status': '  OK  '})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_pass_through_dig_kwargs_to_the_read(self):
        # setup
        expected = {'status': 'default!'}
        op = MapField(key='status', fn=lambda v: f'{v}!', exp=str, default='default')

        # execute -- missing key -> Digger's default kicks in before fn runs
        actual = op({})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_clone_reproduces_equivalent_op(self):
        # setup
        op = MapField(key='status', fn=str.upper)

        # execute
        clone = op.clone()

        # assess
        self.assertEqual(op({'status': 'ok'}), clone({'status': 'ok'}))

        # teardown


if __name__ == '__main__':
    unittest.main()
