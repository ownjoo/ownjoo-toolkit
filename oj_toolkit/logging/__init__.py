"""Standardized logging for ownjoo projects.

Configure once at application startup:

    from oj_toolkit.logging import configure_logging
    configure_logging(service="my-service")           # local: human-readable
    configure_logging(service="my-service", env="prod")  # deployed: JSON lines

Generator decorators:

    from oj_toolkit.logging import timed_generator, timed_async_generator

Log streaming (asyncio apps):

    from oj_toolkit.logging import BroadcastHandler
    handler = BroadcastHandler()
    logging.getLogger().addHandler(handler)
    q = handler.subscribe()   # one queue per connected client
"""

from oj_toolkit.logging.config import configure_logging
from oj_toolkit.logging.consts import LOG_FORMAT
from oj_toolkit.logging.decorators import timed_async_generator, timed_generator
from oj_toolkit.logging.formatters import ColoredHumanFormatter, HumanFormatter, JsonFormatter
from oj_toolkit.logging.handlers import BroadcastHandler

__all__ = [
    'configure_logging',
    'LOG_FORMAT',
    'timed_generator',
    'timed_async_generator',
    'ColoredHumanFormatter',
    'HumanFormatter',
    'JsonFormatter',
    'BroadcastHandler',
]
