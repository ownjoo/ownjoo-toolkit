"""Tests for strip_html()."""

import sys
import unittest
from unittest.mock import patch

try:
    import bs4 as _bs4_module  # noqa: F401

    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

from oj_toolkit.parsing.html import strip_html


@unittest.skipUnless(HAS_BS4, "beautifulsoup4 is not installed -- pip install 'oj-toolkit[html]'")
class TestStripHtml(unittest.TestCase):
    """Tests for strip_html(). Skipped entirely when bs4 isn't installed (it's an
    optional dependency -- see the module docstring in oj_toolkit/parsing/html.py).
    """

    def test_should_extract_visible_text_and_drop_scripts_and_styles(self):
        # setup
        html = (
            '<html><head><style>.x{color:red}</style></head>'
            '<body><script>track();</script><p>Session expired.</p></body></html>'
        )
        expected = 'Session expired.'

        # execute
        actual = strip_html(html)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_prepend_the_title_as_the_first_line_when_present(self):
        # setup
        html = '<html><head><title>Sign In</title></head><body><h1>Please log in</h1></body></html>'
        expected = 'Sign In\nPlease log in'

        # execute
        actual = strip_html(html)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_omit_the_title_line_when_no_title_element_is_present(self):
        # setup
        html = '<html><body><p>hello</p></body></html>'
        expected = 'hello'

        # execute
        actual = strip_html(html)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_drop_default_noise_tags(self):
        # setup
        html = (
            '<html><head><meta charset="utf-8"><link rel="stylesheet" href="x.css">'
            '</head><body><noscript>enable js</noscript>'
            '<svg><circle r="1"/></svg><template><p>tmpl</p></template>'
            '<p>real content</p></body></html>'
        )
        expected = 'real content'

        # execute
        actual = strip_html(html)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_collapse_blank_lines_between_text_blocks(self):
        # setup
        html = '<body>\n\n<p>one</p>\n\n\n<p>two</p>\n\n</body>'
        expected = 'one\ntwo'

        # execute
        actual = strip_html(html)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_empty_string_when_no_text_remains(self):
        # setup
        html = '<html><head><title></title><script>x()</script></head><body></body></html>'
        expected = ''

        # execute
        actual = strip_html(html)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_honor_custom_drop_tags(self):
        # setup
        html = '<body><nav>menu</nav><p>content</p></body>'
        expected = 'content'

        # execute
        actual = strip_html(html, drop_tags=('nav',))

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_keep_nav_text_when_default_drop_tags_are_used(self):
        # setup
        html = '<body><nav>menu</nav><p>content</p></body>'
        expected = 'menu\ncontent'

        # execute
        actual = strip_html(html)

        # assess
        self.assertEqual(expected, actual)

        # teardown


class TestStripHtmlNotInstalled(unittest.TestCase):
    """Tests the optional-dependency error path -- these run regardless of whether
    bs4 is actually installed, by simulating its absence via sys.modules.
    """

    def test_should_raise_import_error_with_install_hint_when_bs4_missing(self):
        # setup / execute / assess
        with patch.dict(sys.modules, {'bs4': None}):
            with self.assertRaises(ImportError) as ctx:
                strip_html('<p>x</p>')
        self.assertIn("pip install 'oj-toolkit[html]'", str(ctx.exception))

        # teardown


if __name__ == '__main__':
    unittest.main()
