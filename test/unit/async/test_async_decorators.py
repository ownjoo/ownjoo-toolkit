"""Tests for the async_timeout decorator."""
import asyncio
import errno
import os
import unittest

from oj_toolkit.asynchronous.decorators import async_timeout


class TestAsyncTimeoutDecorator(unittest.IsolatedAsyncioTestCase):
    """Tests for the async_timeout decorator."""

    async def test_should_return_result_when_call_finishes_in_time(self):
        @async_timeout(seconds=1)
        async def fast():
            return 'done'

        self.assertEqual('done', await fast())

    async def test_should_pass_through_args_and_kwargs(self):
        @async_timeout(seconds=1)
        async def add(a, b, c=0):
            return a + b + c

        self.assertEqual(6, await add(1, 2, c=3))

    async def test_should_raise_timeout_error_when_call_runs_too_long(self):
        @async_timeout(seconds=0.05)
        async def slow():
            await asyncio.sleep(0.3)
            return 'done'

        with self.assertRaises(TimeoutError):
            await slow()

    async def test_should_use_custom_error_message(self):
        @async_timeout(seconds=0.05, error_message='took too long')
        async def slow():
            await asyncio.sleep(0.3)

        with self.assertRaisesRegex(TimeoutError, 'took too long'):
            await slow()

    async def test_should_use_default_error_message_when_not_provided(self):
        @async_timeout(seconds=0.05)
        async def slow():
            await asyncio.sleep(0.3)

        with self.assertRaisesRegex(TimeoutError, os.strerror(errno.ETIME)):
            await slow()

    async def test_should_reraise_exception_from_wrapped_coroutine(self):
        @async_timeout(seconds=1)
        async def raises():
            raise ValueError('bad input')

        with self.assertRaisesRegex(ValueError, 'bad input'):
            await raises()

    async def test_should_actually_cancel_the_coroutine_on_timeout(self):
        """asyncio.wait_for cancels the inner coroutine -- unlike the thread-based
        sync timeout(), it doesn't keep running in the background."""
        cancelled = False

        @async_timeout(seconds=0.05)
        async def slow():
            nonlocal cancelled
            try:
                await asyncio.sleep(0.3)
            except asyncio.CancelledError:
                cancelled = True
                raise

        with self.assertRaises(TimeoutError):
            await slow()
        self.assertTrue(cancelled)


if __name__ == '__main__':
    unittest.main()
