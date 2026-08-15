"""Tests for Map."""

import unittest

from oj_toolkit.ops.control import Map


class TestMap(unittest.TestCase):
    """Tests for Map."""

    def test_should_apply_plain_function_to_item(self):
        # setup
        expected = 'A'
        op = Map(fn=str.upper)

        # execute
        actual = op('a')

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_apply_lambda_to_item(self):
        # setup
        expected = 2
        op = Map(fn=lambda item: item + 1)

        # execute
        actual = op(1)

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
