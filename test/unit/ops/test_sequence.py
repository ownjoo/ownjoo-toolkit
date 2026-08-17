"""Tests for Sequence."""

import unittest

from oj_toolkit.ops.control import Map, Sequence


class TestSequence(unittest.TestCase):
    """Tests for Sequence."""

    def test_should_thread_item_through_ops_in_order(self):
        # setup
        expected = 6
        op = Sequence(ops=[Map(fn=lambda x: x + 1), Map(fn=lambda x: x * 2)])

        # execute
        actual = op(2)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_item_unchanged_for_empty_ops_list(self):
        # setup
        expected = 5
        op = Sequence(ops=[])

        # execute
        actual = op(5)

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
