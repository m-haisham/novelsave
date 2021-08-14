from pathlib import Path

from novelsave.core.entities.novel import Novel
from novelsave.core.services import BaseSaveService, BaseNovelService
from novelsave.core.services.source import BaseSourceGatewayProvider
from novelsave.utils.helpers import string_helper


class SaveService(BaseSaveService):

    def __init__(
            self,
            novels_dir: Path,
            novel_service: BaseNovelService,
            source_provider: BaseSourceGatewayProvider,
    ):
        self.novels_dir = novels_dir
        self.novel_service = novel_service
        self.source_provider = source_provider

    def get_novel_path(self, novel: Novel) -> Path:
        url = self.novel_service.get_primary_url(novel)
        source_gateway = self.source_provider.source_from_url(url)

        source_folder_name = source_gateway.source_name() if source_gateway else ''
        novel_name_slug = string_helper.slugify(novel.title, "_")

        return self.novels_dir / source_folder_name / novel_name_slug
