"""
Constants for parsing and formatting
"""
from enum import Enum

DEFAULT_SEPARATOR: str = ','


class TimeFormats(Enum):
    """Time formats for parsing and formatting"""
    DATE_AND_TIME = '%Y/%m/%d %H:%M:%S'
    ISO8601 = '%Y-%m-%dT%H:%M:%S'
    HTTP = '%a, %d %b %Y %H:%M:%S GMT'
