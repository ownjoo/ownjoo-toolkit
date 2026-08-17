"""Tests for In."""

import unittest

from oj_toolkit.ops.conditions import In


class TestIn(unittest.TestCase):
    """Tests for In."""

    def test_should_return_true_when_field_is_member_of_value(self):
        # setup
        expected = True
        op = In(input='status', value=['ok', 'warn'])

        # execute
        actual = op({'status': 'ok'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_when_field_not_member_of_value(self):
        # setup
        expected = False
        op = In(input='status', value=['ok', 'warn'])

        # execute
        actual = op({'status': 'fail'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_on_incompatible_value_type(self):
        # setup
        expected = False
        op = In(input='status', value=5)

        # execute
        actual = op({'status': 'ok'})

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
