import shutil
from functools import lru_cache
from pathlib import Path
from typing import List, Dict

from loguru import logger
from mako.lookup import TemplateLookup

from novelsave.core.entities.novel import Novel, MetaData, Volume, Chapter
from novelsave.core.services import BaseNovelService, BaseFileService, BasePathService, BaseAssetService
from novelsave.core.services.packagers import BasePackager
from novelsave.utils.helpers import metadata_helper


class WebPackager(BasePackager):
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

    def keywords(self) -> List[str]:
        return ['web', 'html']

    def package(self, novel: Novel) -> Path:
        urls = self.novel_service.get_urls(novel)
        volumes = self.novel_service.get_volumes_with_chapters(novel)
        chapter_count = len([c for cl in volumes.values() for c in cl])
        metadata = self.novel_service.get_metadata(novel)
        logger.debug(f"Preparing to package to web (id={novel.id}, title='{novel.title}', volumes={len(volumes)}, "
                     f"chapters={chapter_count}, metadata={len(metadata)}).")

        toc = self.prepare_toc(volumes)

        base_folder = self.destination(novel)
        base_folder.mkdir(parents=True, exist_ok=True)
        self.compile_index(base_folder, novel, urls, toc, chapter_count, metadata)

        chapters_folder = base_folder / 'chapters'
        chapters_folder.mkdir(parents=True, exist_ok=True)
        for path in chapters_folder.iterdir():
            self.remove_path(path)

        for volume_wrapper in toc:
            for chapter_wrapper in volume_wrapper['chapter_wrappers']:
                self.compile_chapter(chapters_folder, novel, chapter_wrapper)

        logger.debug("Compiled and saved files to web folder (folder='chapters').")

        assets_folder = base_folder / 'assets'
        (assets_folder / 'images').mkdir(parents=True, exist_ok=True)
        for path in assets_folder.iterdir():
            self.remove_path(path)

        self.copy_assets(novel, assets_folder)

        # static files

        (assets_folder / 'css').mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.static_dir / 'web/bootstrap.min.css', assets_folder / 'css')

        (assets_folder / 'js').mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.static_dir / 'web/bootstrap.min.js', assets_folder / 'js')
        logger.debug(f"Copied static to web folder (group='bootstrap').")

        return base_folder

    @lru_cache(maxsize=1)
    def destination(self, novel: Novel):
        path = self.path_service.novel_save_path(novel)
        return path / f'[Web] {path.name}'

    @lru_cache(maxsize=1)
    def path_mapping(self, novel: Novel) -> Dict[int, str]:
        assets = self.asset_service.downloaded_assets(novel)

        return {
            asset.id: f'../assets/images/{Path(asset.path).name}'
            for asset in assets
        }

    @lru_cache(maxsize=1)
    def mapping_dict(self, novel: Novel):
        return self.asset_service.mapping_dict(self.path_mapping(novel))

    def compile_index(self, base_folder: Path, novel, urls, toc, chapter_count, metadata):
        meta_by_name: Dict[str, List[str]] = {}
        for item in metadata:
            meta_by_name.setdefault(item.name, []).append(metadata_helper.display_value(item))

        rendered_data = self.lookup.get_template('index.html.mako').render(
            novel=novel,
            metadata=meta_by_name,
            volume_wrappers=toc,
            has_sections=len(toc) > 1,
            chapter_count=chapter_count,
            sources=[uobject.url for uobject in urls],
        ).encode('utf-8')

        self.file_service.write_bytes(base_folder / 'index.html', rendered_data)
        logger.debug("Compiled and saved files to web folder (file='index.html').")

    def compile_chapter(self, chapter_folder: Path, novel, chapter_wrapper):
        content = self.asset_service.inject_assets(chapter_wrapper['chapter'].content, self.mapping_dict(novel))

        rendered_data = self.lookup.get_template('chapter.html.mako').render(
            novel=novel,
            content=content,
            chapter_wrapper=chapter_wrapper,
        ).encode('utf-8')

        self.file_service.write_bytes(chapter_folder / chapter_wrapper['filename'], rendered_data)

    def copy_assets(self, novel: Novel, assets_folder: Path):
        path_mapping = self.path_mapping(novel)

        assets = self.asset_service.downloaded_assets(novel)
        for asset in assets:
            file = self.path_service.resolve_data_path(asset.path)

            # its only images for now so
            shutil.copy2(file, assets_folder / 'images' / path_mapping[asset.id].lstrip('./'))

        logger.debug(f'Copied assets to web folder (count={len(assets)}).')

    @staticmethod
    def prepare_toc(volumes: Dict[Volume, List[Chapter]]):
        volume_wrappers = []
        for volume, chapters in sorted(volumes.items(), key=lambda v: v.index):

            chapter_wrappers = []
            for chapter in sorted(chapters, key=lambda c: c.index):
                chapter_wrapper = {
                    'order': chapter.index,
                    'chapter': chapter,
                    'filename': f'{str(chapter.index).zfill(4)}.html',
                    'next': None,
                    'previous': None,
                }

                if len(chapter_wrappers) > 0:
                    chapter_wrapper['previous'] = chapter_wrappers[-1]
                elif len(volume_wrappers) > 0:
                    chapter_wrapper['previous'] = volume_wrappers[-1]['chapter_wrappers'][-1]

                if chapter_wrapper['previous'] is not None:
                    chapter_wrapper['previous']['next'] = chapter_wrapper

                chapter_wrappers.append(chapter_wrapper)

            volume_wrappers.append({
                'order': volume.index,
                'volume': volume,
                'chapter_wrappers': chapter_wrappers,
                'id': f'volume-{volume.index}',
            })

        return volume_wrappers

    @staticmethod
    def remove_path(path: Path):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
