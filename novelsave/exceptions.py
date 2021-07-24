class NovelSaveException(Exception):
    """base novelsave exception"""


class SourceNotAvailableException(NovelSaveException):
    """thrown if the source is not available"""


class UnsupportedBrowserException(Exception):
    """"""


class CookieAuthException(Exception):
    """"""


class DownloadLimitException(ValueError):
    """"""


class PathValidationException(ValueError):
    """"""


class NoInputException(Exception):
    """"""


class ResponseException(Exception):
    """"""


class MissingSource(TypeError):
    """"""


class LoginUnavailableException(Exception):
    """"""


class ChapterException(Exception):
    """"""
