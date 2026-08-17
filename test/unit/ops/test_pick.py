"""Tests for Pick."""

import unittest

from oj_toolkit.ops.keys import Pick


class TestPick(unittest.TestCase):
    """Tests for Pick."""

    def test_should_keep_only_listed_keys(self):
        # setup
        expected = {'id': 1, 'status': 'ok'}
        op = Pick(keys=['id', 'status'])

        # execute
        actual = op({'id': 1, 'status': 'ok', 'noise': 'drop me'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_silently_skip_missing_keys(self):
        # setup
        expected = {'id': 1}
        op = Pick(keys=['id', 'missing'])

        # execute
        actual = op({'id': 1})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_empty_dict_for_empty_keys_list(self):
        # setup
        expected = {}
        op = Pick(keys=[])

        # execute
        actual = op({'id': 1})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_not_mutate_the_original_item(self):
        # setup
        original = {'id': 1, 'status': 'ok'}
        op = Pick(keys=['id'])

        # execute
        op(original)

        # assess
        self.assertEqual({'id': 1, 'status': 'ok'}, original)

        # teardown


if __name__ == '__main__':
    unittest.main()
