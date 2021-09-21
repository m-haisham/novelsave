from dataclasses import dataclass

from novelsave.core.dtos import ChapterDTO


class NSException(Exception):
    """base novelsave exception; can be caught and application may proceed once handled"""


class NSError(Exception):
    """base novelsave error; application must not continue once error is thrown"""


@dataclass
class CookieBrowserNotSupportedException(NSException):
    """the specified browser does not support cookie extraction"""
    browser: str


@dataclass
class ContentUpdateFailedException(NSException):
    chapter: ChapterDTO
    exception: Exception


@dataclass
class SourceNotFoundException(NSException):
    """source for the url was not found"""
    url: str


class ToolException(NSException):
    """Generic exception that is raised from command-line tools"""


class PackagingException(NSException):
    """Generic exception that is thrown during packaging"""


class RequirementException(NSException):
    """Raised when a particular requirement is not met"""
