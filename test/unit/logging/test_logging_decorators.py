import logging
import unittest
from asyncio import run
from logging import INFO, getLogger
from typing import AsyncGenerator, Generator

from oj_toolkit.logging.decorators import timed_async_generator, timed_generator


def _reset_root_logger():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.root.setLevel(logging.WARNING)


class TestLoggingDecorators(unittest.TestCase):
    """Tests for timed_generator and timed_async_generator decorators."""

    def setUp(self):
        _reset_root_logger()

    def tearDown(self):
        _reset_root_logger()

    def test_should_import(self):
        @timed_generator(
            log_progress=True, log_level=INFO, log_progress_interval=1, logger=getLogger(__name__)
        )
        def log_something() -> Generator[int, None, None]:
            yield 0

        for each in log_something():
            self.assertIsNotNone(each)


    def test_should_import_async(self):
        async def run_me():
            @timed_async_generator(
                log_progress=True, log_level=INFO, log_progress_interval=1, logger=getLogger(__name__)
            )
            async def log_something() -> AsyncGenerator[int, None]:
                yield 0

            async for each in log_something():
                self.assertIsNotNone(each)
        run(run_me())


    def test_fallback_configure_when_no_logger_provided(self):
        """Decorator should auto-configure logging if root has no handlers."""
        @timed_generator(log_progress=True, log_progress_interval=1)
        def gen():
            yield 1

        self.assertFalse(logging.root.handlers)
        list(gen())
        self.assertTrue(logging.root.handlers, 'configure_logging fallback should have installed a handler')

    def test_fallback_configure_async_when_no_logger_provided(self):
        """Async decorator should auto-configure logging if root has no handlers."""
        async def run_me():
            @timed_async_generator(log_progress=True, log_progress_interval=1)
            async def gen():
                yield 1

            async for _ in gen():
                pass

        self.assertFalse(logging.root.handlers)
        run(run_me())
        self.assertTrue(logging.root.handlers)


if __name__ == '__main__':
    unittest.main()
