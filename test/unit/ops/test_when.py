"""Tests for When."""

import unittest

from oj_toolkit.ops.conditions import Eq
from oj_toolkit.ops.control import Map, When


class TestWhen(unittest.TestCase):
    """Tests for When."""

    def test_should_apply_then_when_condition_true(self):
        # setup
        expected = 'yes'
        op = When(condition=Eq(input='a', value=1), then=Map(lambda item: 'yes'))

        # execute
        actual = op({'a': 1})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_apply_otherwise_when_condition_false(self):
        # setup
        expected = 'no'
        op = When(
            condition=Eq(input='a', value=1),
            then=Map(lambda item: 'yes'),
            otherwise=Map(lambda item: 'no'),
        )

        # execute
        actual = op({'a': 2})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_pass_through_unchanged_when_condition_false_and_no_otherwise(self):
        # setup
        expected = {'a': 2}
        op = When(condition=Eq(input='a', value=1), then=Map(lambda item: 'yes'))

        # execute
        actual = op({'a': 2})

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
