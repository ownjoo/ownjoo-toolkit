"""Tests for Iter."""

import unittest

from oj_toolkit.ops.control import Map
from oj_toolkit.ops.iterate import Iter


class TestIter(unittest.TestCase):
    """Tests for Iter."""

    def test_should_apply_fn_to_each_item(self):
        # setup
        expected = ['A', 'B', 'C']
        op = Iter(fn=str.upper)

        # execute
        actual = list(op(['a', 'b', 'c']))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_empty_generator_for_empty_input(self):
        # setup
        expected = []
        op = Iter(fn=str.upper)

        # execute
        actual = list(op([]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_accept_an_op_instance_as_fn(self):
        # setup
        expected = [2, 3]
        op = Iter(fn=Map(fn=lambda x: x + 1))

        # execute
        actual = list(op([1, 2]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_call_returns_a_generator_not_a_list(self):
        # setup
        op = Iter(fn=str.upper)

        # execute
        actual = op(['a'])

        # assess
        self.assertTrue(hasattr(actual, '__next__'))

        # teardown

    def test_should_raise_type_error_when_fn_omitted(self):
        # execute / assess -- fn is a required constructor argument, no default
        with self.assertRaises(TypeError):
            Iter()  # pylint: disable=no-value-for-parameter

        # teardown

    def test_should_raise_type_error_when_fn_not_callable(self):
        # execute / assess -- construction-time check, not deferred to first call
        with self.assertRaises(TypeError):
            Iter(fn=42)

        # teardown


if __name__ == '__main__':
    unittest.main()
