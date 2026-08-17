"""Tests for FlatMap."""

import unittest

from oj_toolkit.ops.control import Map
from oj_toolkit.ops.iterate import FlatMap


class TestFlatMap(unittest.TestCase):
    """Tests for FlatMap."""

    def test_should_expand_each_item_into_multiple_outputs(self):
        # setup
        expected = [1, 1, 2, 2]
        op = FlatMap(op=Map(fn=lambda item: [item, item]))

        # execute
        actual = list(op([1, 2]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_drop_items_that_expand_to_empty(self):
        # setup
        expected = [1]
        op = FlatMap(op=Map(fn=lambda item: [item] if item == 1 else []))

        # execute
        actual = list(op([1, 2]))

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
