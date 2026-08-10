"""Tests for the timeout decorator."""
import errno
import os
import time
import unittest

from oj_toolkit.timing.decorators import timeout


class TestTimeoutDecorator(unittest.TestCase):
    """Tests for the timeout decorator."""

    def test_should_return_result_when_call_finishes_in_time(self):
        @timeout(seconds=1)
        def fast():
            return 'done'

        self.assertEqual('done', fast())

    def test_should_pass_through_args_and_kwargs(self):
        @timeout(seconds=1)
        def add(a, b, c=0):
            return a + b + c

        self.assertEqual(6, add(1, 2, c=3))

    def test_should_raise_timeout_error_when_call_runs_too_long(self):
        @timeout(seconds=0.05)
        def slow():
            time.sleep(0.3)
            return 'done'

        with self.assertRaises(TimeoutError):
            slow()

    def test_should_use_custom_error_message(self):
        @timeout(seconds=0.05, error_message='took too long')
        def slow():
            time.sleep(0.3)

        with self.assertRaisesRegex(TimeoutError, 'took too long'):
            slow()

    def test_should_use_default_error_message_when_not_provided(self):
        @timeout(seconds=0.05)
        def slow():
            time.sleep(0.3)

        with self.assertRaisesRegex(TimeoutError, os.strerror(errno.ETIME)):
            slow()

    def test_should_reraise_exception_from_wrapped_function(self):
        @timeout(seconds=1)
        def raises():
            raise ValueError('bad input')

        with self.assertRaisesRegex(ValueError, 'bad input'):
            raises()

    def test_should_not_block_caller_after_timeout(self):
        """The caller gets control back promptly, even though the abandoned call
        keeps running on its own daemon thread in the background."""
        @timeout(seconds=0.05)
        def slow():
            time.sleep(0.3)

        start = time.monotonic()
        with self.assertRaises(TimeoutError):
            slow()
        elapsed = time.monotonic() - start
        self.assertLess(elapsed, 0.2)


if __name__ == '__main__':
    unittest.main()
