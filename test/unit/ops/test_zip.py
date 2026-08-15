"""Tests for Zip."""

import unittest

from oj_toolkit.ops.group import Zip


class TestZip(unittest.TestCase):
    """Tests for Zip."""

    def test_should_zip_input_stream_with_other_iterables(self):
        # setup
        expected = [(1, 'a'), (2, 'b')]
        op = Zip(others=[['a', 'b']])

        # execute
        actual = list(op([1, 2]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_truncate_to_shortest_iterable_by_default(self):
        # setup
        expected = [(1, 'a')]
        op = Zip(others=[['a']])

        # execute
        actual = list(op([1, 2]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_raise_on_mismatched_lengths_when_strict(self):
        # setup
        op = Zip(others=[['a']], strict=True)

        # execute / assess
        with self.assertRaises(ValueError):
            list(op([1, 2]))

        # teardown


if __name__ == '__main__':
    unittest.main()
