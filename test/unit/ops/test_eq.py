"""Tests for Eq."""

import unittest

from oj_toolkit.ops.conditions import Eq


class TestEq(unittest.TestCase):
    """Tests for Eq."""

    def test_should_return_true_when_field_equals_value(self):
        # setup
        expected = True
        op = Eq(input='status', value='ok')

        # execute
        actual = op({'status': 'ok'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_when_field_differs_from_value(self):
        # setup
        expected = False
        op = Eq(input='status', value='ok')

        # execute
        actual = op({'status': 'bad'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_when_field_missing(self):
        # setup
        expected = False
        op = Eq(input='status', value='ok')

        # execute
        actual = op({})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_be_registered_under_eq(self):
        # setup
        expected = 'eq'

        # execute
        actual = Eq.type_name

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_clone_reproduces_equivalent_op(self):
        # setup
        op = Eq(input='status', value='ok')

        # execute
        clone = op.clone()

        # assess
        self.assertEqual(op({'status': 'ok'}), clone({'status': 'ok'}))

        # teardown

    def test_should_accept_a_callable_input_instead_of_a_path(self):
        # setup -- input= may be any callable/Op, evaluated fresh against the item,
        # not just a jmespath path resolved via Digger
        expected = True
        op = Eq(input=lambda item: item['n'] * 2, value=10)

        # execute
        actual = op({'n': 5})

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
