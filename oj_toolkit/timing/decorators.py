"""Decorators for enforcing wall-clock time limits on blocking function calls."""

import errno
import os
import threading
from functools import wraps
from typing import Callable, TypeVar

F = TypeVar('F', bound=Callable)

DEFAULT_TIMEOUT_MESSAGE = os.strerror(errno.ETIME)


def timeout(seconds: float = 10, error_message: str | None = None) -> Callable[[F], F]:
    """Decorator that raises TimeoutError if the wrapped call runs longer than `seconds`.

    Runs the wrapped function on a daemon thread and waits up to `seconds` for it to
    finish. This works the same way on every platform and from any calling thread --
    unlike a `signal.alarm`-based timeout, which only works on Unix, only from the
    main thread, and can't be used at all on Windows (`signal.SIGALRM` doesn't exist
    there).

    The trade-off: Python cannot forcibly kill a running thread. If the call doesn't
    finish in time, this raises TimeoutError and returns control to the caller
    immediately, but the wrapped function keeps running to completion on its worker
    thread in the background -- it's abandoned, not aborted. The thread is created
    with `daemon=True` specifically so an abandoned call never blocks interpreter
    shutdown. Use this to stop waiting on a call that's taking too long to *return*,
    not to terminate runaway/CPU-bound work. For coroutines, prefer
    `oj_toolkit.asynchronous.async_timeout`, which actually cancels the inner call.

    Args:
        seconds: Maximum time to wait for the wrapped call to complete. Default: 10.
        error_message: Message for the raised TimeoutError. Default: the OS-provided
            ETIME message (e.g. "Timer expired").

    Returns:
        A decorator that wraps a function with the timeout behavior.

    Example:
        @timeout(seconds=2)
        def slow_call():
            ...

        try:
            slow_call()
        except TimeoutError as e:
            print(f'gave up waiting: {e}')
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            message = error_message if error_message is not None else DEFAULT_TIMEOUT_MESSAGE
            result: list = []
            error: list[BaseException] = []

            def _run():
                try:
                    result.append(func(*args, **kwargs))
                except BaseException as exc:  # pylint: disable=broad-except
                    error.append(exc)

            thread = threading.Thread(target=_run, daemon=True)
            thread.start()
            thread.join(timeout=seconds)
            if thread.is_alive():
                raise TimeoutError(message)
            if error:
                raise error[0]
            return result[0]

        return wrapper

    return decorator
