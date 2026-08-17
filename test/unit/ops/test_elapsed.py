"""Tests for Elapsed."""

import unittest
from unittest.mock import patch

from oj_toolkit.ops.clock import Elapsed
from oj_toolkit.ops.conditions import Gt


class TestElapsed(unittest.TestCase):
    """Tests for Elapsed."""

    def test_should_compute_seconds_elapsed_since_a_path(self):
        # setup
        expected = 300.0
        op = Elapsed(since='created_at')

        # execute
        with patch('oj_toolkit.ops.clock.time.time', return_value=1_700_000_300.0):
            actual = op({'created_at': 1_700_000_000.0})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_accept_a_callable_since(self):
        # setup
        expected = 100.0
        op = Elapsed(since=lambda item: item['start'])

        # execute
        with patch('oj_toolkit.ops.clock.time.time', return_value=1_700_000_100.0):
            actual = op({'start': 1_700_000_000.0})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_compose_with_gt_as_a_condition_input(self):
        # setup
        cond = Gt(input=Elapsed(since='created_at'), value=200)

        # execute / assess
        with patch('oj_toolkit.ops.clock.time.time', return_value=1_700_000_300.0):
            self.assertTrue(cond({'created_at': 1_700_000_000.0}))
            self.assertFalse(cond({'created_at': 1_700_000_299.0}))

        # teardown

    def test_clone_reproduces_equivalent_op(self):
        # setup
        op = Elapsed(since='created_at')

        # execute
        clone = op.clone()

        # assess
        with patch('oj_toolkit.ops.clock.time.time', return_value=1_700_000_300.0):
            self.assertEqual(op({'created_at': 0}), clone({'created_at': 0}))

        # teardown


if __name__ == '__main__':
    unittest.main()
