import json
from typing import Tuple, List, Dict

from novelsave.core.dtos import NovelDTO, ChapterDTO, MetaDataDTO
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
            # a file end in a slash to signify an endpoint
            url=novel_dto.url.rstrip('/') + '/',
        )

        return novel, url

    def update_novel_from_dto(self, novel: Novel, novel_dto: NovelDTO) -> Novel:
        novel.title = novel_dto.title
        novel.author = novel_dto.author
        novel.synopsis = novel_dto.synopsis
        novel.thumbnail_url = novel_dto.thumbnail_url
        novel.lang = novel_dto.lang

        return novel

    def volumes_from_chapter_dtos(self, novel: Novel, chapter_dtos: List[ChapterDTO]) -> Dict[Volume, List[ChapterDTO]]:
        volumes = {}
        for dto in chapter_dtos:
            if dto.volume is None:
                try:
                    volumes[-1][1].append(dto)
                except KeyError:
                    volumes[-1] = (Volume(index=-1, name='_default', novel_id=novel.id), [dto])
            elif len(dto.volume) < 2:
                continue
            else:
                try:
                    volumes[dto.volume[0]][1].append(dto)
                except KeyError:
                    volumes[dto.volume[0]] = (Volume(index=dto.volume[0], name=dto.volume[1], novel_id=novel.id), [dto])

        return {volume: chapters for volume_index, (volume, chapters) in volumes.items()}

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
