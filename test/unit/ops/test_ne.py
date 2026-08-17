"""Tests for Ne."""

import unittest

from oj_toolkit.ops.conditions import Ne


class TestNe(unittest.TestCase):
    """Tests for Ne."""

    def test_should_return_true_when_field_differs_from_value(self):
        # setup
        expected = True
        op = Ne(input='status', value='ok')

        # execute
        actual = op({'status': 'bad'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_when_field_equals_value(self):
        # setup
        expected = False
        op = Ne(input='status', value='ok')

        # execute
        actual = op({'status': 'ok'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_true_when_field_missing(self):
        # setup
        expected = True
        op = Ne(input='status', value='ok')

        # execute
        actual = op({})

        # assess
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
