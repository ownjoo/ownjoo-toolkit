"""Tests for register() and compile()."""

import unittest

from oj_toolkit.ops.base import ItemOp
from oj_toolkit.ops.registry import (  # pylint: disable=redefined-builtin
    _REGISTRY,
    compile,
    register,
)


class TestRegister(unittest.TestCase):
    """Tests for register()."""

    def test_registering_new_name_adds_to_registry(self):
        # setup
        @register('_test_registry_new_name')
        class _Dummy(ItemOp):  # pylint: disable=unused-variable
            def __call__(self, item):
                return item

        # execute
        actual = _REGISTRY['_test_registry_new_name']

        # assess
        self.assertEqual(_Dummy, actual)

        # teardown
        del _REGISTRY['_test_registry_new_name']

    def test_registering_duplicate_class_under_same_name_is_noop(self):
        # setup
        @register('_test_registry_dup_same_class')
        class _Dummy(ItemOp):
            def __call__(self, item):
                return item

        # execute / assess (no exception)
        register('_test_registry_dup_same_class')(_Dummy)

        # teardown
        del _REGISTRY['_test_registry_dup_same_class']

    def test_registering_different_class_under_taken_name_raises(self):
        # setup
        @register('_test_registry_collision')
        class _First(ItemOp):  # pylint: disable=unused-variable
            def __call__(self, item):
                return item

        # execute / assess
        with self.assertRaises(ValueError):
            @register('_test_registry_collision')
            class _Second(ItemOp):  # pylint: disable=unused-variable
                def __call__(self, item):
                    return item

        # teardown
        del _REGISTRY['_test_registry_collision']

    def test_override_true_replaces_existing_registration(self):
        # setup
        @register('_test_registry_override')
        class _First(ItemOp):  # pylint: disable=unused-variable
            def __call__(self, item):
                return item

        # execute
        @register('_test_registry_override', override=True)
        class _Second(ItemOp):
            def __call__(self, item):
                return item

        actual = _REGISTRY['_test_registry_override']

        # assess
        self.assertEqual(_Second, actual)

        # teardown
        del _REGISTRY['_test_registry_override']

    def test_sets_type_name_on_registered_class(self):
        # setup
        @register('_test_registry_type_name')
        class _Dummy(ItemOp):
            def __call__(self, item):
                return item

        # execute
        actual = _Dummy.type_name

        # assess
        self.assertEqual('_test_registry_type_name', actual)

        # teardown
        del _REGISTRY['_test_registry_type_name']


class TestCompile(unittest.TestCase):
    """Tests for compile()."""

    def test_compiles_dict_with_type_key_into_op_instance(self):
        # setup
        expected = 'eq'
        spec = {'type': 'eq', 'input': 'status', 'value': 'ok'}

        # execute
        op = compile(spec)
        actual = op.type_name

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_recursively_compiles_nested_op_specs(self):
        # setup
        spec = {
            'type': 'and',
            'ops': [
                {'type': 'eq', 'input': 'status', 'value': 'ok'},
                {'type': 'not', 'op': {'type': 'eq', 'input': 'status', 'value': 'bad'}},
            ],
        }

        # execute
        op = compile(spec)
        actual = op({'status': 'ok'})

        # assess
        self.assertTrue(actual)

        # teardown

    def test_compiles_list_elements_recursively(self):
        # setup
        spec = [{'type': 'eq', 'input': 'a', 'value': 1}, 'literal']

        # execute
        actual = compile(spec)

        # assess
        self.assertEqual('eq', actual[0].type_name)
        self.assertEqual('literal', actual[1])

        # teardown

    def test_dict_without_type_key_passes_through_unchanged(self):
        # setup
        expected = {'enclosure_id': 'enclosure_id', 'location': 'location'}

        # execute
        actual = compile(expected)

        # assess
        self.assertEqual(expected, actual)
        self.assertIs(expected, actual)

        # teardown

    def test_non_mapping_non_list_literal_passes_through_unchanged(self):
        # setup / execute / assess
        self.assertEqual('a jmespath.path', compile('a jmespath.path'))
        self.assertEqual(5, compile(5))
        self.assertIsNone(compile(None))

        # teardown

    def test_unknown_type_raises_key_error(self):
        # setup
        spec = {'type': '_does_not_exist'}

        # execute / assess
        with self.assertRaises(KeyError):
            compile(spec)

        # teardown


if __name__ == '__main__':
    unittest.main()
