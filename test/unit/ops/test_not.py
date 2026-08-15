"""Tests for Not."""

import unittest

from oj_toolkit.ops.conditions import Eq, Not


class TestNot(unittest.TestCase):
    """Tests for Not."""

    def test_should_negate_true_condition(self):
        # setup
        expected = False
        op = Not(op=Eq(input='status', value='ok'))

        # execute
        actual = op({'status': 'ok'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_negate_false_condition(self):
        # setup
        expected = True
        op = Not(op=Eq(input='status', value='ok'))

        # execute
        actual = op({'status': 'bad'})

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
