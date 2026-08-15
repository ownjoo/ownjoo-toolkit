"""Tests for Join."""

import unittest

from oj_toolkit.ops.group import Join


class TestJoin(unittest.TestCase):
    """Tests for Join."""

    def test_should_merge_matching_records_on_inner_join(self):
        # setup
        expected = [{'id': 1, 'x': 10, 'name': 'a'}]
        op = Join(right=[{'id': 1, 'name': 'a'}, {'id': 2, 'name': 'b'}], on='id')

        # execute
        actual = list(op([{'id': 1, 'x': 10}]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_drop_unmatched_left_records_on_inner_join(self):
        # setup
        expected = []
        op = Join(right=[{'id': 1, 'name': 'a'}], on='id')

        # execute
        actual = list(op([{'id': 99, 'x': 10}]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_keep_unmatched_left_records_on_left_join(self):
        # setup
        expected = [{'id': 99, 'x': 10}]
        op = Join(right=[{'id': 1, 'name': 'a'}], on='id', how='left')

        # execute
        actual = list(op([{'id': 99, 'x': 10}]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_yield_one_row_per_matching_right_record(self):
        # setup
        expected = [
            {'id': 1, 'x': 10, 'name': 'a'},
            {'id': 1, 'x': 10, 'name': 'a2'},
        ]
        op = Join(right=[{'id': 1, 'name': 'a'}, {'id': 1, 'name': 'a2'}], on='id')

        # execute
        actual = list(op([{'id': 1, 'x': 10}]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_support_different_right_on_key(self):
        # setup
        expected = [{'id': 1, 'x': 10, 'user_id': 1, 'name': 'a'}]
        op = Join(right=[{'user_id': 1, 'name': 'a'}], on='id', right_on='user_id')

        # execute
        actual = list(op([{'id': 1, 'x': 10}]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_raise_for_invalid_how(self):
        # setup / execute / assess
        with self.assertRaises(ValueError):
            Join(right=[], on='id', how='outer')

        # teardown


if __name__ == '__main__':
    unittest.main()
