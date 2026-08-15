"""Tests for Extract."""

import unittest

from oj_toolkit.ops.structure import Extract


class TestExtract(unittest.TestCase):
    """Tests for Extract."""

    def test_should_extract_nested_field(self):
        # setup
        expected = 'Alice'
        op = Extract(path='user.name')

        # execute
        actual = op({'user': {'name': 'Alice'}})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_default_when_path_missing(self):
        # setup: exp= is required for default= to kick in -- exp=None (unset) means
        # "accept any type", so validate() never falls back to default (see dig()'s
        # documented behavior in oj_toolkit.parsing.types)
        expected = 'n/a'
        op = Extract(path='user.nickname', exp=str, default='n/a')

        # execute
        actual = op({'user': {'name': 'Alice'}})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_pass_through_dig_kwargs(self):
        # setup
        expected = None
        op = Extract(path='user.age', exp=int)

        # execute
        actual = op({'user': {'age': 'not-an-int'}})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_clone_reproduces_equivalent_op(self):
        # setup
        op = Extract(path='user.name')

        # execute
        clone = op.clone()

        # assess
        self.assertEqual(op({'user': {'name': 'Alice'}}), clone({'user': {'name': 'Alice'}}))

        # teardown


if __name__ == '__main__':
    unittest.main()
