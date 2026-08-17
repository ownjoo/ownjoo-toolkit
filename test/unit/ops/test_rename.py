"""Tests for Rename."""

import unittest

from oj_toolkit.ops.keys import Rename


class TestRename(unittest.TestCase):
    """Tests for Rename."""

    def test_should_rename_listed_keys(self):
        # setup
        expected = {'team': 'a', 'n': 1}
        op = Rename(mapping={'team_id': 'team'})

        # execute
        actual = op({'team_id': 'a', 'n': 1})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_pass_through_unlisted_keys_unchanged(self):
        # setup
        expected = {'id': 1, 'status': 'ok'}
        op = Rename(mapping={'team_id': 'team'})

        # execute
        actual = op({'id': 1, 'status': 'ok'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_not_mutate_the_original_item(self):
        # setup
        original = {'team_id': 'a'}
        op = Rename(mapping={'team_id': 'team'})

        # execute
        op(original)

        # assess
        self.assertEqual({'team_id': 'a'}, original)

        # teardown


if __name__ == '__main__':
    unittest.main()
