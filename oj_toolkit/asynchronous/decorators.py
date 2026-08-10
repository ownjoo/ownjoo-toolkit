"""Decorators for enforcing wall-clock time limits on coroutine calls."""

import asyncio
import errno
import os
from functools import wraps
from typing import Callable, TypeVar

F = TypeVar('F', bound=Callable)

DEFAULT_TIMEOUT_MESSAGE = os.strerror(errno.ETIME)


def async_timeout(seconds: float = 10, error_message: str | None = None) -> Callable[[F], F]:
    """Decorator that raises TimeoutError if the wrapped coroutine runs longer than `seconds`.

    Thin wrapper around `asyncio.timeout()`, asyncio's built-in deadline context
    manager -- no threads, signals, or extra dependencies needed. Unlike the
    thread-based `oj_toolkit.timing.timeout` (for blocking/sync calls), a timed-out
    coroutine here is actually cancelled: past the deadline, `asyncio.timeout()`
    throws `asyncio.CancelledError` into it at its next `await` point, so a
    well-behaved coroutine stops promptly instead of continuing to run in the
    background.

    Args:
        seconds: Maximum time to wait for the coroutine to complete. Default: 10.
        error_message: Message for the raised TimeoutError. Default: the OS-provided
            ETIME message (e.g. "Timer expired").

    Returns:
        A decorator that wraps an async function with the timeout behavior.

    Example:
        @async_timeout(seconds=2)
        async def slow_call():
            await asyncio.sleep(5)

        try:
            await slow_call()
        except TimeoutError as e:
            print(f'gave up waiting: {e}')

    Note:
        `asyncio.timeout()` can also be used directly as an `async with` block to
        share one deadline across several awaits, rather than bounding a single
        named function -- reach for that when you need more than "time out this
        one call". Requires Python 3.11+.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            message = error_message if error_message is not None else DEFAULT_TIMEOUT_MESSAGE
            try:
                async with asyncio.timeout(seconds):
                    return await func(*args, **kwargs)
            except TimeoutError:
                raise TimeoutError(message) from None

        return wrapper

    return decorator
