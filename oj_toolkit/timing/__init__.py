"""Wall-clock timeout utilities for blocking (synchronous) calls.

For coroutines, use `oj_toolkit.asynchronous.async_timeout` instead -- it cancels
the inner call on timeout rather than abandoning a background thread.

Usage:
    from oj_toolkit.timing import timeout

    @timeout(seconds=5)
    def slow_call():
        ...
"""

from oj_toolkit.timing.decorators import timeout

__all__ = ['timeout']
