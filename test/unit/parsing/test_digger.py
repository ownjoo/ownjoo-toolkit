"""Tests for Digger."""

import re
import unittest

from jmespath.exceptions import ParseError

from oj_toolkit.parsing.types import Digger


class TestDigger(unittest.TestCase):
    """Tests for Digger."""

    # Digger: a bound path can be reused as a callable across multiple src objects
    def test_should_reuse_digger_across_multiple_sources(self):
        # setup
        get_name = Digger(path='user.name', exp=str, default='')
        records: list = [{'user': {'name': 'Alice'}}, {'user': {'name': 'Bob'}}]

        # execute
        actual = [get_name(record) for record in records]

        # assess
        self.assertEqual(actual, ['Alice', 'Bob'])

    # Digger: an invalid jmespath expression fails at construction time, not first call
    def test_should_fail_fast_on_invalid_digger_expression(self):
        # execute/assess
        with self.assertRaises(ParseError):
            Digger(path='user[..name')

    # Digger: a string pattern is pre-compiled at construction time
    def test_should_precompile_string_pattern_in_digger(self):
        # setup/execute
        digger = Digger(path='mac', exp=str, pattern=r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}')

        # assess
        self.assertIsInstance(digger.kwargs['pattern'], re.Pattern)


if __name__ == '__main__':
    unittest.main()
