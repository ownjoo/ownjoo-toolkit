"""Tests for Resolve."""

import unittest

from oj_toolkit.ops.conditions import Eq
from oj_toolkit.ops.structure import Resolve


class _Response:  # pylint: disable=too-few-public-methods
    """Stand-in for something like httpx.Response -- attributes and a zero-arg method."""

    status_code = 200
    ok = True

    def json(self):
        return {'data': {'id': 1}}


class TestResolve(unittest.TestCase):
    """Tests for Resolve."""

    def test_should_resolve_a_plain_attribute(self):
        # setup
        expected = 200
        op = Resolve(path='status_code')

        # execute
        actual = op(_Response())

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_auto_call_a_method_and_continue_resolving(self):
        # setup
        expected = 1
        op = Resolve(path='json.data.id')

        # execute
        actual = op(_Response())

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_default_for_unresolvable_path(self):
        # setup
        expected = 'n/a'
        op = Resolve(path='missing.path', default='n/a')

        # execute
        actual = op(_Response())

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_compose_with_eq_as_a_condition_input(self):
        # setup
        cond = Eq(input=Resolve(path='status_code'), value=200)

        # execute / assess
        self.assertTrue(cond(_Response()))

        # teardown


if __name__ == '__main__':
    unittest.main()
