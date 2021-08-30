from pathlib import Path
from typing import Dict, Union
from urllib.parse import urlparse

from novelsave.core.entities.novel import Novel, Asset
from novelsave.core.services import BasePathService, BaseNovelService
from novelsave.core.services.source import BaseSourceService
from novelsave.exceptions import SourceNotFoundException
from novelsave.utils.helpers import string_helper


class PathService(BasePathService):

    def __init__(
            self,
            data_dir: Path,
            novels_dir: Path,
            division_rules: Dict[str, str],
            novel_service: BaseNovelService,
            source_service: BaseSourceService,
    ):
        self.data_dir = data_dir
        self.novels_dir = novels_dir
        self.division_rules = division_rules
        self.novel_service = novel_service
        self.source_service = source_service

    def divide(self, path: Path) -> Path:
        parent = path.parent / self.division_rules.get(path.suffix, '')
        return parent.resolve() / path.name

    def novel_save_path(self, novel: Novel) -> Path:
        url = self.novel_service.get_primary_url(novel)
        try:
            source_gateway = self.source_service.source_from_url(url)
            source_folder_name = source_gateway.name
        except SourceNotFoundException:
            source_folder_name = ''

        novel_name_slug = string_helper.slugify(novel.title, "_")

        return (self.novels_dir / source_folder_name / novel_name_slug).resolve()

    def novel_data_path(self, novel: Novel) -> Path:
        return self.data_dir / str(novel.id)

    def asset_path(self, novel: Novel, asset: Asset) -> Path:
        parse_result = urlparse(novel.thumbnail_url)
        suffix = Path(parse_result.path).suffix
        file = Path(str(asset.id) + suffix)

        return self.novel_data_path(novel) / self.divide(file)

    def thumbnail_path(self, novel: Novel) -> Path:
        suffix = Path(novel.thumbnail_url).suffix

        return self.data_dir / str(novel.id) / f'cover{suffix}'

    def resolve_data_path(self, r_path: Union[Path, str]) -> Path:
        return self.data_dir / str(r_path).lstrip('.').lstrip('/\\')

    def relative_to_novel_dir(self, path: Path) -> Path:
        return path.relative_to(self.novels_dir)

    def relative_to_data_dir(self, path: Path) -> Path:
        return path.relative_to(self.data_dir)
