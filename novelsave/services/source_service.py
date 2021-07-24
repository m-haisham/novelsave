from typing import Union

from novelsave_sources.exceptions import UnknownSourceException
from novelsave_sources.sources.novel.source import Source
from novelsave_sources.utils import parse_source

from novelsave.exceptions import SourceNotAvailableException
from novelsave.view_models import Novel, Chapter


def require_source(func):
    """checks if the source is available, otherwise raises [SourceNotAvailableException]"""
    def decorated(self, *args, **kwargs):
        if type(self.source) == SourceNotAvailableException:
            raise self.source

        return func(self, *args, **kwargs)

    return decorated


class SourceService(object):
    """
    TODO add source update checker (pip?)
    TODO add source updater (pip?)
    """
    source: Union[Source, SourceNotAvailableException]

    def __init__(self, novel_url: str):
        try:
            self.source = parse_source(novel_url)
        except UnknownSourceException as e:
            self.source = SourceNotAvailableException(str(e))

    @require_source
    def is_search_capable(self) -> bool:
        """denotes whether the source has search capability"""
        return self.source.__search__

    @require_source
    def is_login_capable(self) -> bool:
        """denotes whether the source has login capability"""
        return self.source.__login__

    @require_source
    def search(self, keyword: str):
        """search the source with a specific keyword for a novel"""
        return self.source.search(keyword)  # TODO convert

    @require_source
    def login(self, username: str, password: str):
        """login to the source website, making available services or novels which might otherwise be absent"""
        return self.source.login(username, password)

    @require_source
    def novel_by_url(self, url: str) -> Novel:
        """scrape and parse a novel by its url"""

    @require_source
    def update_chapter_content(self, chapter: Chapter):
        """update a chapter's content by following its url"""
