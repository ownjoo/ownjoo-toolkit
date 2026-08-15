"""Tests for Exists."""

import unittest

from oj_toolkit.ops.conditions import Exists


class TestExists(unittest.TestCase):
    """Tests for Exists."""

    def test_should_return_true_when_field_present(self):
        # setup
        expected = True
        op = Exists(input='status')

        # execute
        actual = op({'status': 'ok'})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_when_field_missing(self):
        # setup
        expected = False
        op = Exists(input='status')

        # execute
        actual = op({})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_false_when_field_explicitly_none(self):
        # setup
        expected = False
        op = Exists(input='status')

        # execute
        actual = op({'status': None})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_clone_reproduces_equivalent_op(self):
        # setup
        op = Exists(input='status')

        # execute
        clone = op.clone()

        # assess
        self.assertEqual(op({'status': 'ok'}), clone({'status': 'ok'}))

        # teardown


if __name__ == '__main__':
    unittest.main()
