from collections import defaultdict
from typing import Dict, List

from bs4 import BeautifulSoup
from loguru import logger
from sqlalchemy import update, delete
from sqlalchemy.orm import Session

from novelsave.core.dtos import ChapterDTO
from novelsave.core.entities.constants import AssetTypes
from novelsave.core.entities.novel import Asset, Novel
from novelsave.core.services import BaseAssetService, BasePathService
from novelsave.utils.helpers import url_helper


class AssetService(BaseAssetService):

    def __init__(
            self,
            session: Session,
            path_service: BasePathService,
    ):
        self.session = session
        self.path_service = path_service

    def downloaded_assets(self, novel: Novel) -> List[Asset]:
        downloaded = []
        for asset in novel.assets:
            if asset.path is None:
                continue

            file = self.path_service.resolve_data_path(asset.path)
            if not file.exists() or not file.is_file():
                continue

            downloaded.append(asset)

        return downloaded

    def pending_assets(self, novel: Novel) -> List[Asset]:
        pending = []
        for asset in novel.assets:
            if asset.path is None:
                pending.append(asset)
                continue

            file = self.path_service.resolve_data_path(asset.path)
            if not file.exists() or not file.is_file():
                pending.append(asset)

        return pending

    def update_asset_path(self, asset: Asset):
        self.session.execute(update(Asset).where(Asset.id == asset.id).values(path=asset.path))
        self.session.commit()

    def delete_assets_of_novel(self, novel: Novel):
        self.session.execute(delete(Asset).where(Asset.novel_id == novel.id))
        self.session.commit()

    def update_assets(self, novel: Novel, assets: List[Asset]) -> Dict[str, Asset]:
        indexed_assets = {a.url: a for a in novel.assets}
        indexed_specific = {}

        assets_to_add = []
        for asset in assets:
            try:
                indexed_specific[asset.url] = indexed_assets[asset.url]
            except KeyError:
                indexed_specific[asset.url] = asset
                assets_to_add.append(asset)

        # we only interact with the database if we have something to add
        # this is [expected] to be more performant
        if assets_to_add:
            logger.debug(f'Adding newly found assets (count={len(assets_to_add)}).')
            self.session.add_all(assets_to_add)
            self.session.flush()
        else:
            logger.debug(f"Skipping adding assets ({novel.id=}, reason='No assets to add')")

        return indexed_specific

    def collect_assets(self, novel: Novel, chapter: ChapterDTO) -> str:

        # using default parser since lxml inserts <html> and <body> tags
        # those would have to be removed since the input doesnt require to have them
        # so its better to not insert them at all
        soup = BeautifulSoup(chapter.content, 'html.parser')

        assets = []
        for img in soup.select('img'):
            src = img.get('src', default=None)
            alt = img.get('alt', default='[Unspecified]')
            if not src:
                continue

            url = url_helper.absolute_url(src, chapter.url)
            asset = Asset(
                name=alt,
                url=url,
                type_id=AssetTypes.IMAGE,
                novel_id=novel.id,
            )

            assets.append(asset)

        logger.debug(f"Identified asset images (novel='{novel.title}', count={len(assets)}).")
        if not assets:
            logger.debug(f"Skipped further asset processing (novel='{novel.title}', reason='No assets identified')")
            return chapter.content

        indexed_assets = self.update_assets(novel, assets)
        for img in soup.select('img'):
            src = img.get('src', default=None)
            if not src:
                continue

            url = url_helper.absolute_url(src, chapter.url)
            img['src'] = f'{{id{indexed_assets[url].id}}}'

        logger.debug(f"Embedded asset markers (chapter='{chapter.title}').")

        return str(soup)

    def mapping_dict(self, path_mapping: Dict[int, str]):
        return defaultdict(
            str,
            {f'id{key}': path for key, path in path_mapping.items()}
        )

    def inject_assets(self, html: str, mapping_dict: Dict[int, str]):
        return html.format_map(mapping_dict)
