from typing import Tuple

from novelsave.core.dtos import NovelDTO
from novelsave.core.entities.novel import Novel, NovelUrl


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
            url=novel_dto.url,
        )

        return novel, url
