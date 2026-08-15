"""Tests for Gt."""

import unittest

from oj_toolkit.ops.conditions import Gt


class TestGt(unittest.TestCase):
    """Tests for Gt."""

    def test_should_return_true_when_field_greater_than_value(self):
        # setup
        expected = True
        op = Gt(input='n', value=5)

        # execute
        actual = op({'n': 10})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_when_field_not_greater_than_value(self):
        # setup
        expected = False
        op = Gt(input='n', value=5)

        # execute
        actual = op({'n': 5})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_on_incompatible_types(self):
        # setup
        expected = False
        op = Gt(input='n', value=5)

        # execute
        actual = op({'n': 'not-a-number'})

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
