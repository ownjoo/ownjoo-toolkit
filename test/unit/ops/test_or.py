"""Tests for Or."""

import unittest

from oj_toolkit.ops.conditions import Eq, Or


class TestOr(unittest.TestCase):
    """Tests for Or."""

    def test_should_return_true_when_any_op_true(self):
        # setup
        expected = True
        op = Or(ops=[Eq(input='status', value='ok'), Eq(input='status', value='warn')])

        # execute
        actual = op({'status': 'warn'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_when_all_ops_false(self):
        # setup
        expected = False
        op = Or(ops=[Eq(input='status', value='ok'), Eq(input='status', value='warn')])

        # execute
        actual = op({'status': 'fail'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_for_empty_ops_list(self):
        # setup
        expected = False
        op = Or(ops=[])

        # execute
        actual = op({})

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
