"""Tests for Omit."""

import unittest

from oj_toolkit.ops.keys import Omit


class TestOmit(unittest.TestCase):
    """Tests for Omit."""

    def test_should_drop_listed_keys(self):
        # setup
        expected = {'id': 1}
        op = Omit(keys=['status', 'noise'])

        # execute
        actual = op({'id': 1, 'status': 'ok', 'noise': 'drop me'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_ignore_keys_not_present(self):
        # setup
        expected = {'id': 1}
        op = Omit(keys=['missing'])

        # execute
        actual = op({'id': 1})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_full_copy_for_empty_keys_list(self):
        # setup
        expected = {'id': 1, 'status': 'ok'}
        op = Omit(keys=[])

        # execute
        actual = op({'id': 1, 'status': 'ok'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_not_mutate_the_original_item(self):
        # setup
        original = {'id': 1, 'status': 'ok'}
        op = Omit(keys=['status'])

        # execute
        op(original)

        # assess
        self.assertEqual({'id': 1, 'status': 'ok'}, original)

        # teardown


if __name__ == '__main__':
    unittest.main()
