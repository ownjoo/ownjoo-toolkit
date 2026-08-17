"""Tests for Fanout."""

import unittest

from oj_toolkit.ops.conditions import In
from oj_toolkit.ops.structure import Extract, Fanout


class TestFanout(unittest.TestCase):
    """Tests for Fanout."""

    def test_should_build_dict_from_named_ops(self):
        # setup
        expected = {'status': 'ok', 'is_ok': True}
        op = Fanout(status=Extract(path='status'), is_ok=In(input='status', value=['ok']))

        # execute
        actual = op({'status': 'ok'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_empty_dict_for_no_ops(self):
        # setup
        expected = {}
        op = Fanout()

        # execute
        actual = op({'status': 'ok'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_clone_reproduces_equivalent_op(self):
        # setup
        op = Fanout(status=Extract(path='status'))

        # execute
        clone = op.clone()

        # assess
        self.assertEqual(op({'status': 'ok'}), clone({'status': 'ok'}))

        # teardown


if __name__ == '__main__':
    unittest.main()
