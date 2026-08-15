"""Tests for GroupBy."""

import unittest

from oj_toolkit.ops.group import GroupBy


class TestGroupBy(unittest.TestCase):
    """Tests for GroupBy."""

    def test_should_group_items_by_jmespath_key(self):
        # setup
        expected = {
            'ok': [{'status': 'ok', 'n': 1}, {'status': 'ok', 'n': 2}],
            'bad': [{'status': 'bad', 'n': 3}],
        }
        op = GroupBy(key='status')

        # execute
        actual = op([{'status': 'ok', 'n': 1}, {'status': 'ok', 'n': 2}, {'status': 'bad', 'n': 3}])

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_group_items_by_callable_key(self):
        # setup
        expected = {0: [2, 4], 1: [1, 3]}
        op = GroupBy(key=lambda item: item % 2)

        # execute
        actual = op([1, 2, 3, 4])

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_empty_dict_for_empty_input(self):
        # setup
        expected = {}
        op = GroupBy(key='status')

        # execute
        actual = op([])

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_call_returns_dict_not_generator(self):
        # setup
        op = GroupBy(key='status')

        # execute
        actual = op([{'status': 'ok'}])

        # assess
        self.assertIsInstance(actual, dict)

        # teardown


if __name__ == '__main__':
    unittest.main()
