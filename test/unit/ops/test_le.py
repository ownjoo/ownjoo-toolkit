"""Tests for Le."""

import unittest

from oj_toolkit.ops.conditions import Le


class TestLe(unittest.TestCase):
    """Tests for Le."""

    def test_should_return_true_when_field_equal_to_value(self):
        # setup
        expected = True
        op = Le(input='n', value=5)

        # execute
        actual = op({'n': 5})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_when_field_greater_than_value(self):
        # setup
        expected = False
        op = Le(input='n', value=5)

        # execute
        actual = op({'n': 6})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_on_incompatible_types(self):
        # setup
        expected = False
        op = Le(input='n', value=5)

        # execute
        actual = op({'n': 'not-a-number'})

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
