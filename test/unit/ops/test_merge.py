"""Tests for Merge."""

import unittest

from oj_toolkit.ops.control import Map
from oj_toolkit.ops.structure import Merge


class TestMerge(unittest.TestCase):
    """Tests for Merge."""

    def test_should_shallow_merge_dict_results(self):
        # setup
        expected = {'a': 1, 'b': 2}
        op = Merge(ops=[Map(fn=lambda item: {'a': 1}), Map(fn=lambda item: {'b': 2})])

        # execute
        actual = op({})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_let_later_op_overwrite_earlier_on_key_collision(self):
        # setup
        expected = {'a': 2}
        op = Merge(ops=[Map(fn=lambda item: {'a': 1}), Map(fn=lambda item: {'a': 2})])

        # execute
        actual = op({})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_empty_dict_for_empty_ops_list(self):
        # setup
        expected = {}
        op = Merge(ops=[])

        # execute
        actual = op({})

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
