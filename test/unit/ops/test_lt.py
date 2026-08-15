"""Tests for Lt."""

import unittest

from oj_toolkit.ops.conditions import Lt


class TestLt(unittest.TestCase):
    """Tests for Lt."""

    def test_should_return_true_when_field_less_than_value(self):
        # setup
        expected = True
        op = Lt(input='n', value=5)

        # execute
        actual = op({'n': 1})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_when_field_not_less_than_value(self):
        # setup
        expected = False
        op = Lt(input='n', value=5)

        # execute
        actual = op({'n': 5})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_on_incompatible_types(self):
        # setup
        expected = False
        op = Lt(input='n', value=5)

        # execute
        actual = op({'n': 'not-a-number'})

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
