"""Tests for And."""

import unittest

from oj_toolkit.ops.conditions import And, Eq, Exists


class TestAnd(unittest.TestCase):
    """Tests for And."""

    def test_should_return_true_when_all_ops_true(self):
        # setup
        expected = True
        op = And(ops=[Eq(input='status', value='ok'), Exists(input='id')])

        # execute
        actual = op({'status': 'ok', 'id': 1})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_when_any_op_false(self):
        # setup
        expected = False
        op = And(ops=[Eq(input='status', value='ok'), Exists(input='id')])

        # execute
        actual = op({'status': 'ok'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_true_for_empty_ops_list(self):
        # setup
        expected = True
        op = And(ops=[])

        # execute
        actual = op({})

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
