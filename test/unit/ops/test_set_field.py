"""Tests for SetField."""

import unittest

from oj_toolkit.ops.keys import SetField


class TestSetField(unittest.TestCase):
    """Tests for SetField."""

    def test_should_set_key_to_literal_value(self):
        # setup
        expected = {'id': 1, 'checked': True}
        op = SetField(key='checked', value=True)

        # execute
        actual = op({'id': 1})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_overwrite_existing_key(self):
        # setup
        expected = {'status': 'overwritten'}
        op = SetField(key='status', value='overwritten')

        # execute
        actual = op({'status': 'ok'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_not_mutate_the_original_item(self):
        # setup
        original = {'id': 1}
        op = SetField(key='checked', value=True)

        # execute
        op(original)

        # assess
        self.assertEqual({'id': 1}, original)

        # teardown


if __name__ == '__main__':
    unittest.main()
