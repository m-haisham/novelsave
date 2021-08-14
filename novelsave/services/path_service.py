from pathlib import Path

from urllib.parse import urlparse

from novelsave.core.entities.novel import Novel
from novelsave.core.services import BasePathService, BaseNovelService
from novelsave.core.services.source import BaseSourceGatewayProvider
from novelsave.utils.helpers import string_helper


class PathService(BasePathService):

    def __init__(
            self,
            data_dir: Path,
            novels_dir: Path,
            novel_service: BaseNovelService,
            source_provider: BaseSourceGatewayProvider,
    ):
        self.data_dir = data_dir
        self.novels_dir = novels_dir
        self.novel_service = novel_service
        self.source_provider = source_provider

    def get_novel_path(self, novel: Novel) -> Path:
        url = self.novel_service.get_primary_url(novel)
        source_gateway = self.source_provider.source_from_url(url)

        source_folder_name = source_gateway.source_name() if source_gateway else ''
        novel_name_slug = string_helper.slugify(novel.title, "_")

        return self.novels_dir / source_folder_name / novel_name_slug

    def get_thumbnail_path(self, novel: Novel) -> Path:
        result = urlparse(novel.thumbnail_url)
        suffix = Path(result.path).suffix
        suffix = suffix if suffix else '.jpg'

        return self.data_dir / str(novel.id) / f'cover{suffix}'

    def relative_to_data_dir(self, path: Path) -> Path:
        return path.relative_to(self.data_dir)
