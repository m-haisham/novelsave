import base64
import mimetypes
import shutil
from functools import lru_cache
from pathlib import Path
from typing import List, Dict

from loguru import logger
from mako.lookup import TemplateLookup

from novelsave.core.entities.novel import Novel, MetaData, Volume, Chapter
from novelsave.core.services import BaseNovelService, BaseFileService, BasePathService, BaseAssetService
from novelsave.core.services.packagers import BasePackager
from novelsave.utils.helpers import metadata_helper, string_helper


class HtmlPackager(BasePackager):
    def __init__(
            self,
            static_dir: Path,
            novel_service: BaseNovelService,
            file_service: BaseFileService,
            path_service: BasePathService,
            asset_service: BaseAssetService,
    ):
        self.static_dir = static_dir
        self.novel_service = novel_service
        self.file_service = file_service
        self.path_service = path_service
        self.asset_service = asset_service

        self.lookup = TemplateLookup(directories=[self.static_dir / 'web/templates'])

    @property
    def priority(self):
        return 1

    def keywords(self) -> List[str]:
        return ['html', 'web']

    def package(self, novel: Novel) -> Path:
        urls = self.novel_service.get_urls(novel)
        volumes = self.novel_service.get_volumes_with_chapters(novel)
        chapter_count = len([c for cl in volumes.values() for c in cl])
        metadata = self.novel_service.get_metadata(novel)
        logger.debug(f"Preparing to package to web (id={novel.id}, title='{novel.title}', volumes={len(volumes)}, "
                     f"chapters={chapter_count}, metadata={len(metadata)}).")

        html_file = self.destination(novel)
        html_file.parent.mkdir(parents=True, exist_ok=True)

        toc = self.prepare_toc(novel, volumes)

        meta_by_name: Dict[str, List[str]] = {}
        for item in metadata:
            meta_by_name.setdefault(item.name, []).append(metadata_helper.display_value(item))

        rendered_data = self.lookup.get_template('index.html.mako').render(
            novel=novel,
            metadata=meta_by_name,
            volume_wrappers=toc,
            chapter_count=chapter_count,
            sources=[uobject.url for uobject in urls],
            static=self.prepare_static(),
        ).encode('utf-8')
        logger.debug(f"Rendered html file (size='{string_helper.format_bytes(len(rendered_data))}').")

        self.file_service.write_bytes(html_file, rendered_data)

        logger.debug(f"Compiled and saved html file (file='{self.path_service.relative_to_novel_dir(html_file)}').")
        return html_file

    @lru_cache(maxsize=1)
    def destination(self, novel: Novel):
        path = self.path_service.novel_save_path(novel)
        return path / f'{path.name}.html'

    @lru_cache(maxsize=1)
    def path_mapping(self, novel: Novel) -> Dict[int, str]:
        assets = self.asset_service.downloaded_assets(novel)

        mapping = {}
        for asset in assets:
            file_data = self.file_service.read_bytes(self.path_service.resolve_data_path(asset.path))
            base64_data = base64.b64decode(file_data)
            mimetype, encoding = mimetypes.guess_type(asset.path)

            mapping[asset.id] = f"data:{mimetype};base64,{base64_data.decode('utf-8')}"

        return mapping

    @lru_cache(maxsize=1)
    def mapping_dict(self, novel: Novel):
        return self.asset_service.mapping_dict(self.path_mapping(novel))

    def prepare_toc(self, novel: Novel, volumes: Dict[Volume, List[Chapter]]):
        volume_wrappers = []
        for volume, chapters in sorted(volumes.items(), key=lambda v: v.index):

            chapter_wrappers = [
                {
                    'order': chapter.index,
                    'chapter': chapter,
                    'filename': f'{str(chapter.index).zfill(4)}.html',
                    'content': self.asset_service.inject_assets(chapter.content, self.mapping_dict(novel)),
                    'id': f'chapter-{chapter.index}'
                }
                for chapter in sorted(chapters, key=lambda c: c.index)
            ]

            volume_wrappers.append({
                'order': volume.index,
                'volume': volume,
                'chapter_wrappers': chapter_wrappers,
                'id': f'volume-{volume.index}',
            })

        logger.debug(f"Constructed table of contents for web (volumes={len(volumes)}).")

        return volume_wrappers

    def prepare_static(self):
        static = {
            'bootstrap.min.css': self.file_service.read_str(self.static_dir / 'web/bootstrap.min.css'),
            'bootstrap.min.js': self.file_service.read_str(self.static_dir / 'web/bootstrap.min.js'),
        }

        logger.debug(f"Retrieved static data (count={len(static)}).")
        return static
