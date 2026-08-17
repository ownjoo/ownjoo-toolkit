"""Tests for resolve()."""

import unittest

from oj_toolkit.parsing.resolve import resolve


class _Response:  # pylint: disable=too-few-public-methods
    """Stand-in for something like httpx.Response -- attributes and a zero-arg method."""

    status_code = 200
    headers = {'content-type': 'application/json'}

    def json(self):
        return {'data': {'id': 1, 'items': [10, 20, 30]}}


class TestResolve(unittest.TestCase):
    """Tests for resolve()."""

    def test_should_resolve_a_plain_attribute(self):
        # setup
        expected = 200

        # execute
        actual = resolve(_Response(), 'status_code')

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_resolve_a_dict_valued_attribute_by_key(self):
        # setup
        expected = 'application/json'

        # execute
        actual = resolve(_Response(), 'headers.content-type')

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_auto_call_a_method_and_continue_resolving(self):
        # setup
        expected = 1

        # execute
        actual = resolve(_Response(), 'json.data.id')

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_resolve_a_list_index_segment(self):
        # setup
        expected = 20

        # execute
        actual = resolve(_Response(), 'json.data.items.1')

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_navigate_a_plain_dict_like_an_object(self):
        # setup
        expected = 5

        # execute
        actual = resolve({'a': {'b': 5}}, 'a.b')

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_default_for_missing_attribute(self):
        # setup
        expected = 'n/a'

        # execute
        actual = resolve(_Response(), 'does_not_exist', default='n/a')

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_default_for_missing_intermediate_segment(self):
        # setup
        expected = 'n/a'

        # execute
        actual = resolve(_Response(), 'json.missing.deeper', default='n/a')

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_none_default_when_not_specified(self):
        # setup / execute
        actual = resolve(_Response(), 'does_not_exist')

        # assess
        self.assertIsNone(actual)

        # teardown

    def test_should_support_custom_separator(self):
        # setup
        expected = 1

        # execute
        actual = resolve(_Response(), 'json/data/id', sep='/')

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
