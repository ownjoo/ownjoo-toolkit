"""Tests for Broadcast."""

import unittest

from oj_toolkit.ops.structure import Broadcast


class TestBroadcast(unittest.TestCase):
    """Tests for Broadcast."""

    def test_should_merge_parent_fields_into_each_child(self):
        # setup
        parent = {
            'enclosure_id': 'abc',
            'location': 'rack1',
            'blades': [{'serial': 'b1'}, {'serial': 'b2'}],
        }
        expected = [
            {'enclosure_id': 'abc', 'location': 'rack1', 'serial': 'b1'},
            {'enclosure_id': 'abc', 'location': 'rack1', 'serial': 'b2'},
        ]
        op = Broadcast(
            children_path='blades',
            fields={'enclosure_id': 'enclosure_id', 'location': 'location'},
        )

        # execute
        actual = op(parent)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_empty_list_when_no_children(self):
        # setup
        expected = []
        op = Broadcast(children_path='blades', fields={})

        # execute
        actual = op({'blades': []})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_empty_list_when_children_path_missing(self):
        # setup
        expected = []
        op = Broadcast(children_path='blades', fields={})

        # execute
        actual = op({})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_clone_reproduces_equivalent_op(self):
        # setup
        parent = {'enclosure_id': 'abc', 'blades': [{'serial': 'b1'}]}
        op = Broadcast(children_path='blades', fields={'enclosure_id': 'enclosure_id'})

        # execute
        clone = op.clone()

        # assess
        self.assertEqual(op(parent), clone(parent))

        # teardown


if __name__ == '__main__':
    unittest.main()
