from typing import Dict, List

from bs4 import BeautifulSoup
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from novelsave.core.dtos import ChapterDTO
from novelsave.core.entities.constants import AssetTypes
from novelsave.core.entities.novel import Asset, Novel
from novelsave.core.services import BaseAssetService


class AssetService(BaseAssetService):

    def __init__(self, session: Session):
        self.session = session

    def update_assets(self, novel: Novel, assets: List[Asset]) -> Dict[str, Asset]:
        stmt = select(Asset).where(Asset.novel_id == novel.id)
        indexed_assets = {a.url: a for a in self.session.execute(stmt).scalars().all()}
        indexed_specific = {}

        assets_to_add = []
        for asset in assets:
            try:
                indexed_specific[asset.url] = indexed_assets[asset.url]
            except KeyError:
                indexed_specific[asset.url] = asset
                assets_to_add.append(asset)

        logger.debug(f'Adding newly found assets (count={len(assets_to_add)}).')
        self.session.add_all(assets_to_add)
        self.session.flush()

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

            assets.append(Asset(name=alt, url=src, type_id=AssetTypes.IMAGE, novel_id=novel.id))

        logger.debug(f'Identified asset images (novel={novel.title}, count={len(assets)}).')

        indexed_assets = self.update_assets(novel, assets)
        for img in soup.select('img'):
            src = img.get('src', default=None)
            if not src:
                continue

            img['src'] = '{id%d}' % indexed_assets[src].id

        logger.debug(f'Embedded asset markers (chapter={chapter.title}).')

        return str(soup)

    def inject_assets(self, html: str, path_mapping: Dict[int, str]):
        pass
