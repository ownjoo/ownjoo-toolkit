"""Tests for Op."""

import unittest

from oj_toolkit.ops.base import ItemOp, Op, StreamOp


class DummyItemOp(ItemOp):
    """Concrete ItemOp for testing Op's shared behavior."""

    def __init__(self, value=None, label='x'):
        self.value = value
        self.label = label

    def __call__(self, item):
        return self.value


class TestOp(unittest.TestCase):
    """Tests for Op."""

    def test_call_raises_not_implemented_on_base_op(self):
        # setup
        op = Op()

        # execute / assess
        with self.assertRaises(NotImplementedError):
            op(1)

        # teardown

    def test_describe_includes_class_name(self):
        # setup
        op = DummyItemOp(value=1)

        # execute
        actual = op.describe()

        # assess
        self.assertIn('DummyItemOp', actual)

        # teardown

    def test_describe_includes_constructor_attrs(self):
        # setup
        op = DummyItemOp(value=1, label='y')

        # execute
        actual = op.describe()

        # assess
        self.assertIn('value=1', actual)
        self.assertIn("label='y'", actual)

        # teardown

    def test_repr_matches_describe(self):
        # setup
        op = DummyItemOp(value=1)

        # execute
        actual = repr(op)

        # assess
        self.assertEqual(op.describe(), actual)

        # teardown

    def test_clone_reproduces_equivalent_op(self):
        # setup
        op = DummyItemOp(value=1, label='y')

        # execute
        clone = op.clone()

        # assess
        self.assertIsNot(op, clone)
        self.assertEqual(op.value, clone.value)
        self.assertEqual(op.label, clone.label)

        # teardown

    def test_clone_applies_overrides(self):
        # setup
        op = DummyItemOp(value=1, label='y')

        # execute
        clone = op.clone(value=2)

        # assess
        self.assertEqual(2, clone.value)
        self.assertEqual('y', clone.label)

        # teardown

    def test_item_op_and_stream_op_are_op_subclasses(self):
        # setup / execute / assess
        self.assertTrue(issubclass(ItemOp, Op))
        self.assertTrue(issubclass(StreamOp, Op))

        # teardown


if __name__ == '__main__':
    unittest.main()
