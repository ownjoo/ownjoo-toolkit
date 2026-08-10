"""Comprehensive exception surfacing for an async Python service.

Python has **five** distinct places where an exception can silently disappear:

1. Top-level uncaught exceptions           → ``sys.excepthook``
2. Exceptions in background threads        → ``threading.excepthook``
3. "Unraisable" exceptions (``__del__``)   → ``sys.unraisablehook``
4. Asyncio event-loop callback errors      → ``loop.set_exception_handler``
5. Tasks that raise and are never awaited  → ``logging`` at GC time
   + ``ResourceWarning`` about unawaited coroutines.

Default Python handlers for most of these log to ``stderr`` with minimal
context, or (for #5) simply print a warning. On a server running under
uvicorn with log capture and an SSE broadcast, those messages can easily
be missed or misattributed.

This module installs one consolidated handler for every category above
that emits a structured ``ERROR`` log via the standard ``logging`` system.
Anything emitted via ``logging`` reaches stdout *and* any attached
handlers (SSE broadcasts, file loggers, etc.) so the error is visible
everywhere you look.

Usage
-----

Call once at process startup, before any async task can spin up:

    from oj_toolkit.diagnostics import install_exception_visibility
    install_exception_visibility()

Idempotent. Safe in tests — each test run gets the handlers installed
once; subsequent calls are no-ops.
"""

from __future__ import annotations

import asyncio
import logging
import sys
import threading
import warnings

logger = logging.getLogger('oj_toolkit.diagnostics')

_INSTALLED = False


def install_exception_visibility(*, strict_async_warnings: bool = True) -> None:
    """Install hooks so no exception can disappear silently.

    Parameters
    ----------
    strict_async_warnings:
        If ``True`` (default), asyncio's ``ResourceWarning``/``RuntimeWarning``
        about unretrieved task exceptions and unawaited coroutines are
        promoted from "ignored-by-default" to "always shown". Set to
        ``False`` if you have many legitimate fire-and-forget tasks you
        deliberately don't await.
    """
    global _INSTALLED  # pylint: disable=global-statement
    if _INSTALLED:
        return
    _INSTALLED = True

    _install_sys_excepthook()
    _install_threading_excepthook()
    _install_unraisablehook()
    _install_asyncio_exception_handler()

    if strict_async_warnings:
        warnings.filterwarnings('always', category=ResourceWarning)
        warnings.filterwarnings('always', category=RuntimeWarning)

    # Asyncio emits the "Task exception was never retrieved" message via
    # logging at ERROR level already. Ensure its logger isn't silenced.
    logging.getLogger('asyncio').setLevel(logging.WARNING)

    logger.info(
        'exception visibility installed '
        '(sys.excepthook + threading.excepthook + '
        'sys.unraisablehook + asyncio loop handler)'
    )


# ------------------------------------------------------------------ sys.excepthook

def _install_sys_excepthook() -> None:
    _prev = sys.excepthook

    def _hook(exc_type, exc, tb):
        if issubclass(exc_type, KeyboardInterrupt):
            _prev(exc_type, exc, tb)
            return
        logger.error('uncaught top-level exception', exc_info=(exc_type, exc, tb))

    sys.excepthook = _hook


# ------------------------------------------------------------------ threading.excepthook

def _install_threading_excepthook() -> None:
    def _hook(args: threading.ExceptHookArgs) -> None:
        if issubclass(args.exc_type, SystemExit):
            return
        thread_name = args.thread.name if args.thread is not None else 'unknown'
        logger.error(
            'uncaught exception in thread %r',
            thread_name,
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    threading.excepthook = _hook


# ------------------------------------------------------------------ sys.unraisablehook

def _install_unraisablehook() -> None:
    def _hook(unraisable) -> None:
        logger.error(
            'unraisable exception in %r',
            unraisable.object,
            exc_info=(unraisable.exc_type, unraisable.exc_value, unraisable.exc_traceback),
        )

    sys.unraisablehook = _hook


# ------------------------------------------------------------------ asyncio

def _install_asyncio_exception_handler() -> None:
    """Install on the currently-running loop (if any) AND wrap the event-loop
    policy so every subsequently-created loop inherits the handler."""
    try:
        current = asyncio.get_running_loop()
        current.set_exception_handler(_asyncio_exception_handler)
    except RuntimeError:
        pass  # no running loop yet; policy-level install below takes care of it.

    policy = asyncio.get_event_loop_policy()
    _prev_new = policy.new_event_loop

    def _wrapped_new() -> asyncio.AbstractEventLoop:
        loop = _prev_new()
        loop.set_exception_handler(_asyncio_exception_handler)
        return loop

    policy.new_event_loop = _wrapped_new  # type: ignore[method-assign]


def _asyncio_exception_handler(
    loop: asyncio.AbstractEventLoop,  # pylint: disable=unused-argument
    context: dict,
) -> None:
    """Default handler for exceptions in asyncio callbacks and tasks.

    ``loop`` is part of the callback signature expected by
    ``loop.set_exception_handler``; we don't use it because all logging
    already happens via the standard logging system.
    """
    message = context.get('message', 'asyncio exception (no message)')
    exception = context.get('exception')
    task = context.get('task') or context.get('future')
    extras = {k: v for k, v in context.items() if k not in ('message', 'exception')}

    if exception is not None:
        logger.error(
            'asyncio exception: %s (task=%r) extras=%r',
            message,
            task,
            extras,
            exc_info=(type(exception), exception, exception.__traceback__),
        )
    else:
        logger.error(
            'asyncio error: %s (task=%r) extras=%r',
            message,
            task,
            extras,
        )


__all__ = [
    'install_exception_visibility',
    'strict_visibility',
    'ExpectedError',
]


# ======================================================================
# Test-mode strict visibility
# ======================================================================

# An exception type tests can raise (or mark) to acknowledge that an
# ERROR-level log was expected during the test.
class ExpectedError(Exception):
    """Marker base for exceptions a test explicitly expects to log."""


import contextlib  # noqa: E402 — kept near its user
import os  # noqa: E402


@contextlib.contextmanager
def strict_visibility(*, fail_on_error_log: bool = True):  # pylint: disable=too-many-locals
    """Context manager for tests: route all silent channels to a collector,
    assert the collector is empty at exit.

    Fails (``AssertionError``) if:

    - any ERROR+ log record was emitted during the block (unless
      ``fail_on_error_log=False``);
    - any asyncio task raised an exception that wasn't awaited;
    - any background thread died with an uncaught exception.

    Intended use inside a pytest fixture — see ``pytest_strict_plugin`` below
    for the drop-in conftest helper.

    Honors ``OJ_DEBUG_STRICT=1``: when set, re-raises the first captured
    exception immediately instead of collecting them, so interactive
    debugging sees the failure at the source rather than at fixture teardown.
    """
    install_exception_visibility()

    errors: list[logging.LogRecord] = []
    task_failures: list[BaseException] = []
    thread_failures: list[tuple[type, BaseException, object]] = []
    immediate = os.environ.get('OJ_DEBUG_STRICT', '').lower() in ('1', 'true', 'yes')

    class _ErrorCollector(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
            if record.levelno >= logging.ERROR:
                errors.append(record)
                if immediate:
                    exc = record.exc_info[1] if record.exc_info else None
                    raise AssertionError(
                        f'ERROR log during strict_visibility: {record.getMessage()}'
                    ) from exc

    handler = _ErrorCollector()
    logging.getLogger().addHandler(handler)

    _prev_thread_hook = threading.excepthook

    def _thread_hook(args: threading.ExceptHookArgs) -> None:
        thread_failures.append((args.exc_type, args.exc_value, args.thread))
        _prev_thread_hook(args)

    threading.excepthook = _thread_hook

    loop: asyncio.AbstractEventLoop | None = None
    _prev_loop_handler = None
    try:
        loop = asyncio.get_running_loop()
        _prev_loop_handler = loop.get_exception_handler()

        def _collect(loop_, context):
            exc = context.get('exception')
            if exc is not None:
                task_failures.append(exc)
            if _prev_loop_handler is not None:
                _prev_loop_handler(loop_, context)
            else:
                _asyncio_exception_handler(loop_, context)

        loop.set_exception_handler(_collect)
    except RuntimeError:
        pass  # not in an async context — threading + log hooks still apply

    try:
        yield
    finally:
        logging.getLogger().removeHandler(handler)
        threading.excepthook = _prev_thread_hook
        if loop is not None:
            loop.set_exception_handler(_prev_loop_handler)

        problems = []
        if fail_on_error_log and errors:
            for r in errors:
                problems.append(f'ERROR log: {r.name}: {r.getMessage()}')
        for exc in task_failures:
            problems.append(f'asyncio task failure: {type(exc).__name__}: {exc}')
        for exc_type, exc, thread in thread_failures:
            name = getattr(thread, 'name', 'unknown')
            problems.append(f'thread {name!r} died: {exc_type.__name__}: {exc}')

        if problems:
            raise AssertionError(
                'strict visibility detected silent failures:\n  ' + '\n  '.join(problems)
            )


def pytest_strict_plugin():
    """Return a pytest-autouse fixture that wraps every test in ``strict_visibility``.

    Usage (in the project's ``conftest.py``)::

        from oj_toolkit.diagnostics import pytest_strict_plugin

        pytest_plugins = ['oj_toolkit.diagnostics']
        strict_visibility_fixture = pytest_strict_plugin()

    Or, equivalently, copy the fixture into the conftest directly::

        import pytest
        from oj_toolkit.diagnostics import strict_visibility

        @pytest.fixture(autouse=True)
        def _strict_visibility():
            with strict_visibility():
                yield

    Individual tests opt out by marking with ``@pytest.mark.expect_error``.
    """
    # pylint: disable-next=import-outside-toplevel
    import pytest  # local import so the module doesn't hard-require pytest at import time

    @pytest.fixture(autouse=True)
    def _strict_visibility(request):
        marker = request.node.get_closest_marker('expect_error')
        if marker is not None:
            # Test explicitly opts out. Install visibility but don't fail on errors.
            install_exception_visibility()
            yield
            return
        with strict_visibility():
            yield

    return _strict_visibility
