"""Tests for Resolver."""

import unittest

from oj_toolkit.parsing.resolve import Resolver


class _Response:  # pylint: disable=too-few-public-methods
    """Stand-in for something like httpx.Response."""

    status_code = 200

    def json(self):
        return {'data': {'id': 1}}


class TestResolver(unittest.TestCase):
    """Tests for Resolver."""

    def test_should_resolve_when_called(self):
        # setup
        expected = 200
        get_status = Resolver(path='status_code')

        # execute
        actual = get_status(_Response())

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_be_reusable_across_multiple_objects(self):
        # setup
        expected = [1, 1]
        get_id = Resolver(path='json.data.id')

        # execute
        actual = [get_id(_Response()), get_id(_Response())]

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_apply_default_on_missing_path(self):
        # setup
        expected = 'n/a'
        get_missing = Resolver(path='missing.path', default='n/a')

        # execute
        actual = get_missing(_Response())

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_repr_includes_path(self):
        # setup
        resolver = Resolver(path='status_code')

        # execute
        actual = repr(resolver)

        # assess
        self.assertIn('status_code', actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
