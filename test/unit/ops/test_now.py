"""Tests for Now."""

import unittest
from unittest.mock import patch

from oj_toolkit.ops.clock import Now


class TestNow(unittest.TestCase):
    """Tests for Now."""

    def test_should_return_current_time(self):
        # setup
        expected = 1_700_000_000.0
        op = Now()

        # execute
        with patch('oj_toolkit.ops.clock.time.time', return_value=expected):
            actual = op({'irrelevant': 'item'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_ignore_the_item(self):
        # setup
        op = Now()

        # execute
        with patch('oj_toolkit.ops.clock.time.time', return_value=1.0):
            first = op({'a': 1})
            second = op(None)

        # assess
        self.assertEqual(first, second)

        # teardown


if __name__ == '__main__':
    unittest.main()
