from requests import Response


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
