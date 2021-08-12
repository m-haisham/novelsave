from typing import Tuple, List

from novelsave_sources.sources.novel.source import Source

from novelsave.core import dtos
from novelsave.utils.adapters import SourceAdapter


class SourceGateway(object):
    """
    TODO add source update checker (pip?)
    TODO add source updater (pip?)
    """
    def __init__(self, source: Source, source_adapter: SourceAdapter):
        self.source = source
        self.source_adapter = source_adapter

    def source_name(self) -> str:
        return self.source.__name__

    def is_search_capable(self) -> bool:
        """denotes whether the source has search capability"""
        return self.source.__search__

    def is_login_capable(self) -> bool:
        """denotes whether the source has login capability"""
        return self.source.__login__

    def search(self, keyword: str):
        """search the source with a specific keyword for a novel"""
        self.source.search(keyword)

    def login(self, username: str, password: str):
        """login to the source website, making available services or novels which might otherwise be absent"""
        self.source.login(username, password)

    def novel_by_url(self, url: str) -> Tuple[dtos.NovelDTO, List[dtos.ChapterDTO], List[dtos.MetaDataDTO]]:
        """scrape and parse a novel by its url"""
        novel, chapters, metadata = self.source.novel(url)

        internal_novel = self.source_adapter.novel_to_internal(novel)
        internal_chapters = [self.source_adapter.chapter_to_internal(c) for c in chapters]
        internal_metadata = [self.source_adapter.metadata_to_internal(m) for m in metadata]

        return internal_novel, internal_chapters, internal_metadata

    def update_chapter_content(self, chapter: dtos.ChapterDTO):
        """update a chapter's content by following its url"""
        source_chapter = self.source_adapter.chapter_to_external(chapter)
        self.source.chapter(source_chapter)

        self.source_adapter.chapter_content_to_internal(source_chapter, chapter)
