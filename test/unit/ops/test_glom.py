"""Tests for Glom."""

import sys
import unittest
from unittest.mock import patch

from oj_toolkit.ops.conditions import Eq
from oj_toolkit.ops.glom_op import Glom
from oj_toolkit.ops.iterate import Iter

try:
    import glom as _glom_module

    HAS_GLOM = True
except ImportError:
    HAS_GLOM = False


@unittest.skipUnless(HAS_GLOM, "glom is not installed -- pip install 'oj-toolkit[glom]'")
class TestGlom(unittest.TestCase):
    """Tests for Glom. Skipped entirely when glom isn't installed (it's an optional
    dependency -- see the module docstring in oj_toolkit/ops/glom_op.py).
    """

    def test_should_extract_via_a_dotted_string_spec(self):
        # setup
        expected = 'c'
        op = Glom(spec='a.b')

        # execute
        actual = op({'a': {'b': 'c'}})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_build_a_dict_via_a_dict_spec(self):
        # setup
        expected = {'val': 'c', 'items': [1, 2, 3]}
        op = Glom(spec={'val': 'a.b', 'items': 'x'})

        # execute
        actual = op({'a': {'b': 'c'}, 'x': [1, 2, 3]})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_forward_default_kwarg_to_glom(self):
        # setup
        expected = 'n/a'
        op = Glom(spec='missing', default='n/a')

        # execute
        actual = op({'a': {'b': 'c'}})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_raise_glom_error_when_no_default_given(self):
        # setup
        op = Glom(spec='missing')

        # execute / assess
        with self.assertRaises(_glom_module.GlomError):
            op({'a': {'b': 'c'}})

        # teardown

    def test_should_support_t_object_method_calls_with_arguments(self):
        # setup -- the actual gap this op fills: resolve() only auto-calls callables
        # with no arguments, glom's T object can pass real arguments along a path
        class Pager:  # pylint: disable=too-few-public-methods
            """Stand-in object whose method takes a real argument."""

            def get_page(self, n):
                return f'page-{n}'

        expected = 'page-2'
        op = Glom(spec=_glom_module.T.get_page(2))

        # execute
        actual = op(Pager())

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_compose_with_iter(self):
        # setup
        expected = ['ok', 'bad']
        op = Iter(fn=Glom(spec='a.b'))

        # execute
        actual = list(op([{'a': {'b': 'ok'}}, {'a': {'b': 'bad'}}]))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_compose_as_a_condition_input(self):
        # setup
        expected = True
        op = Eq(input=Glom(spec='a.b'), value='ok')

        # execute
        actual = op({'a': {'b': 'ok'}})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_clone_reproduces_equivalent_op(self):
        # setup
        op = Glom(spec='a.b', default='n/a')

        # execute
        clone = op.clone()

        # assess
        self.assertEqual(op({'a': {'b': 'c'}}), clone({'a': {'b': 'c'}}))
        self.assertEqual(op({}), clone({}))

        # teardown


class TestGlomNotInstalled(unittest.TestCase):
    """Tests the optional-dependency error path -- these run regardless of whether
    glom is actually installed, by simulating its absence via sys.modules.
    """

    def test_should_raise_import_error_with_install_hint_when_glom_missing(self):
        # setup / execute / assess
        with patch.dict(sys.modules, {'glom': None}):
            with self.assertRaises(ImportError) as ctx:
                Glom(spec='a.b')
        self.assertIn("pip install 'oj-toolkit[glom]'", str(ctx.exception))

        # teardown


if __name__ == '__main__':
    unittest.main()
