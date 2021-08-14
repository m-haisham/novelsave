from typing import Tuple, List

from novelsave_sources.sources.novel.source import Source

from ...core import dtos
from ...core.services.source import BaseSourceGateway
from ...utils.adapters import SourceAdapter


class SourceGateway(BaseSourceGateway):
    def __init__(self, source: Source, source_adapter: SourceAdapter):
        self.source = source
        self.source_adapter = source_adapter

    def source_name(self) -> str:
        return self.source.__class__.__name__

    def is_search_capable(self) -> bool:
        return self.source.__search__

    def is_login_capable(self) -> bool:
        return self.source.__login__

    def search(self, keyword: str):
        self.source.search(keyword)

    def login(self, username: str, password: str):
        self.source.login(username, password)

    def novel_by_url(self, url: str) -> Tuple[dtos.NovelDTO, List[dtos.ChapterDTO], List[dtos.MetaDataDTO]]:
        novel, chapters, metadata = self.source.novel(url)

        internal_novel = self.source_adapter.novel_to_internal(novel)
        internal_chapters = [self.source_adapter.chapter_to_internal(c) for c in chapters]
        internal_metadata = [self.source_adapter.metadata_to_internal(m) for m in metadata]

        return internal_novel, internal_chapters, internal_metadata

    def update_chapter_content(self, chapter: dtos.ChapterDTO) -> dtos.ChapterDTO:
        source_chapter = self.source_adapter.chapter_to_external(chapter)
        self.source.chapter(source_chapter)
        self.source_adapter.chapter_content_to_internal(source_chapter, chapter)

        return chapter
