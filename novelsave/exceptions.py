from dataclasses import dataclass


class NovelSaveException(Exception):
    """base novelsave exception"""


@dataclass
class CookieBrowserNotSupportedException(NovelSaveException):
    """the specified browser does not support cookie extraction"""
    browser: str


@dataclass
class SourceNotFoundException(NovelSaveException):
    """source for the url was not found"""
    url: str


class NovelSourceNotFoundException(SourceNotFoundException):
    """source of the specific type novel was not found for the url"""


class MetaDataSourceNotFoundException(SourceNotFoundException):
    """source of the specific type metadata was not found for the url"""
