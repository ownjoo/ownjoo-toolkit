"""Tests for Filter."""

import unittest

from oj_toolkit.ops.conditions import In
from oj_toolkit.ops.iterate import Filter


class TestFilter(unittest.TestCase):
    """Tests for Filter."""

    def test_should_keep_only_matching_items(self):
        # setup
        expected = [{'status': 'ok'}]
        op = Filter(condition=In(input='status', value=['ok', 'warn']))

        # execute
        actual = list(op([{'status': 'ok'}, {'status': 'fail'}]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_empty_when_nothing_matches(self):
        # setup
        expected = []
        op = Filter(condition=In(input='status', value=['ok']))

        # execute
        actual = list(op([{'status': 'fail'}]))

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
