from typing import Union, Tuple, List

from novelsave_sources.exceptions import UnknownSourceException
from novelsave_sources.sources.novel.source import Source
from novelsave_sources import models as source_models
from novelsave_sources.utils import parse_source

from novelsave.exceptions import SourceNotAvailableException
from novelsave.models import source_models as im
from novelsave.utils.adapters import SourceAdapter


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

    def __init__(self, novel_url: str, source_adapter: SourceAdapter):
        try:
            self.source = parse_source(novel_url)
        except UnknownSourceException as e:
            self.source = SourceNotAvailableException(str(e))

        self.source_adapter = source_adapter

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
        self.source.search(keyword)

    @require_source
    def login(self, username: str, password: str):
        """login to the source website, making available services or novels which might otherwise be absent"""
        self.source.login(username, password)

    @require_source
    def novel_by_url(self, url: str) -> Tuple[im.Novel, List[im.Chapter], List[im.MetaData]]:
        """scrape and parse a novel by its url"""
        novel, chapters, metadata = self.source.novel(url)

        internal_novel = self.source_adapter.novel_to_internal(novel)
        internal_chapters = [self.source_adapter.chapter_to_internal(c) for c in chapters]
        internal_metadata = [self.source_adapter.metadata_to_internal(m) for m in metadata]

        return internal_novel, internal_chapters, internal_metadata

    @require_source
    def update_chapter_content(self, chapter: im.Chapter):
        """update a chapter's content by following its url"""
        source_chapter = self.source_adapter.chapter_from_internal(chapter)
        self.source.chapter(source_chapter)

        self.source_adapter.chapter_content_to_internal(source_chapter, chapter)
