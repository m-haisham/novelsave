from .metasource import MetaSource
from .wlnupdates import WlnUpdates
from .novelupdates import NovelUpdates
from ..exceptions import MissingSource

meta_sources = [
    WlnUpdates,
    NovelUpdates,
]


def parse_metasource(url):
    """
    create neta source object to which the :param url: belongs to

    :return: meta source object
    """
    for source in meta_sources:
        if source.of(url):
            return source()

    raise MissingSource(url, f'"{url}" does not belong to any available metadata source')