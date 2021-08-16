from dataclasses import dataclass


class NovelSaveException(Exception):
    """base novelsave exception"""


@dataclass
class CookieBrowserNotSupportedException(NovelSaveException):
    """the specified browser does not support cookie extraction"""
    browser: str
