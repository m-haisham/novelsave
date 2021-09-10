import json
from pathlib import Path
from typing import Tuple, List, Dict

from novelsave.core.dtos import NovelDTO, ChapterDTO, MetaDataDTO, VolumeDTO
from novelsave.core.entities.novel import Novel, NovelUrl, Chapter, Volume, MetaData


class DTOAdapter:

    def novel_from_dto(self, novel_dto: NovelDTO) -> Tuple[Novel, NovelUrl]:
        novel = Novel(
            title=novel_dto.title,
            author=novel_dto.author,
            synopsis=novel_dto.synopsis,
            thumbnail_url=novel_dto.thumbnail_url,
            lang=novel_dto.lang,
        )

        url = NovelUrl(
            # ensure trailing forward slash, it is preferred that a uri that isn't
            # a file end in a slash to signify a path
            url=novel_dto.url.rstrip('/') + ('/' if Path(novel_dto.url).suffix else ''),
        )

        return novel, url

    def update_novel_from_dto(self, novel: Novel, novel_dto: NovelDTO) -> Novel:
        novel.title = novel_dto.title
        novel.author = novel_dto.author
        novel.synopsis = novel_dto.synopsis
        novel.thumbnail_url = novel_dto.thumbnail_url
        novel.lang = novel_dto.lang

        return novel

    def volumes_from_dto(self, novel: Novel, volume_dtos: List[VolumeDTO]) -> Dict[Volume, List[ChapterDTO]]:
        return {
            Volume(
                id=dto.id,
                index=dto.index,
                name=dto.name,
                novel_id=novel.id,
            ): dto.chapters
            for dto in volume_dtos
        }

    def chapter_from_dto(self, volume: Volume, chapter_dto: ChapterDTO) -> Chapter:
        return Chapter(
            index=chapter_dto.index,
            title=chapter_dto.title,
            url=chapter_dto.url,
            volume_id=volume.id,
        )

    def chapter_to_dto(self, chapter: Chapter):
        return ChapterDTO(
            index=chapter.index,
            title=chapter.title,
            url=chapter.url,
        )

    def metadata_from_dto(self, novel: Novel, metadata_dto: MetaDataDTO) -> MetaData:
        return MetaData(
            name=metadata_dto.name,
            value=metadata_dto.value,
            namespace=metadata_dto.namespace,
            others=json.dumps(metadata_dto.others),
            novel_id=novel.id,
        )
