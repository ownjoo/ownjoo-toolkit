"""Tests for Xor."""

import unittest

from oj_toolkit.ops.conditions import Eq, Xor


class TestXor(unittest.TestCase):
    """Tests for Xor."""

    def test_should_return_true_when_exactly_one_op_true(self):
        # setup
        expected = True
        op = Xor(ops=[Eq(input='a', value=1), Eq(input='b', value=1)])

        # execute
        actual = op({'a': 1, 'b': 2})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_when_all_ops_false(self):
        # setup
        expected = False
        op = Xor(ops=[Eq(input='a', value=1), Eq(input='b', value=1)])

        # execute
        actual = op({'a': 2, 'b': 2})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_use_parity_semantics_not_exactly_one(self):
        # setup: 3 true operands -- parity XOR is True, "exactly one true" would be False
        expected = True
        op = Xor(ops=[Eq(input='a', value=1), Eq(input='b', value=1), Eq(input='c', value=1)])

        # execute
        actual = op({'a': 1, 'b': 1, 'c': 1})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_when_two_of_three_ops_true(self):
        # setup: even count of true operands -- parity XOR is False
        expected = False
        op = Xor(ops=[Eq(input='a', value=1), Eq(input='b', value=1), Eq(input='c', value=1)])

        # execute
        actual = op({'a': 1, 'b': 1, 'c': 2})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_for_empty_ops_list(self):
        # setup
        expected = False
        op = Xor(ops=[])

        # execute
        actual = op({})

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
