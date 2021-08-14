import os
import sys
from typing import Optional

import requests
from dependency_injector.wiring import inject, Provide
from loguru import logger

from novelsave.cli.helpers.source import get_source_gateway
from novelsave.containers import Application
from novelsave.core.entities.novel import Novel
from novelsave.core.services import BasePathService, BaseNovelService
from novelsave.services import NovelService, FileService
from novelsave.utils.adapters import DTOAdapter
from novelsave.utils.concurrent import ConcurrentActionsController


@inject
def create_novel(
        url: str,
        novel_service: NovelService = Provide[Application.services.novel_service],
) -> Novel:
    """
    retrieve information about the novel from webpage and insert novel into database.
    this includes chapter list and metadata.
    """
    source_gateway = get_source_gateway(url)

    logger.info(f'Retrieving novel (url={url})...')
    novel_dto, chapter_dtos, metadata_dtos = source_gateway.novel_by_url(url)

    novel = novel_service.insert_novel(novel_dto)
    novel_service.insert_chapters(novel, chapter_dtos)
    novel_service.insert_metadata(novel, metadata_dtos)

    logger.info(f'New novel (id={novel.id}, title={novel.title}, chapters={len(chapter_dtos)})')
    return novel


@inject
def update_novel(
        novel: Novel,
        novel_service: NovelService = Provide[Application.services.novel_service],
):
    url = novel_service.get_primary_url(novel)
    logger.debug(f'Using primary url. (url={url})')

    source_gateway = get_source_gateway(url)

    logger.info(f'Retrieving novel (url={url})...')
    novel_dto, chapter_dtos, metadata_dtos = source_gateway.novel_by_url(url)

    novel_service.update_novel(novel, novel_dto)
    novel_service.update_chapters(novel, chapter_dtos)
    novel_service.update_metadata(novel, metadata_dtos)

    logger.info(f'Updated novel (id={novel.id}, title={novel.title}, chapters={len(chapter_dtos)})')
    return novel


@inject
def download_thumbnail(
        novel: Novel,
        force: bool = False,
        novel_service: BaseNovelService = Provide[Application.services.novel_service],
        file_service: FileService = Provide[Application.services.file_service],
        path_service: BasePathService = Provide[Application.services.path_service],
):
    thumbnail_path = path_service.get_thumbnail_path(novel)
    if not force and thumbnail_path.exists() and thumbnail_path.is_file():
        logger.info(f'Skipped thumbnail download (title={novel.title})')
        return

    logger.debug(f'Attempting thumbnail download (title={novel.title}, url={novel.thumbnail_url})')
    response = requests.get(novel.thumbnail_url)
    if not response.ok:
        logger.info(f'Error during thumbnail download (title={novel.title}, status_code={response.status_code})')
        return

    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    file_service.write_bytes(thumbnail_path, response.content)
    novel_service.set_thumbnail_asset(novel, path_service.relative_to_data_dir(thumbnail_path))

    logger.info(f'Downloaded thumbnail image (title={novel.title}, thumbnail_path={novel.thumbnail_path})')


@inject
def download_pending(
        novel: Novel,
        limit: Optional[int],
        novel_service: NovelService = Provide[Application.services.novel_service],
        dto_adapter: DTOAdapter = Provide[Application.adapters.dto_adapter],
):
    chapters = novel_service.get_pending_chapters(novel, limit)
    if not chapters:
        logger.info(f'Novel (title={novel.title}) has no pending chapters.')

    url = novel_service.get_primary_url(novel)
    logger.debug(f'Using primary novel url. (url={url})')

    source_gateway = get_source_gateway(url)

    # setup controller
    controller = ConcurrentActionsController(min(os.cpu_count(), len(chapters)), source_gateway.update_chapter_content)
    for chapter in chapters:
        controller.add(dto_adapter.chapter_to_dto(chapter))

    logger.info(f'Downloading pending chapters. (count={len(chapters)}, threads={len(controller.threads)})...')
    for chapter_dto in controller.iter():
        novel_service.update_content(chapter_dto)
        logger.debug(f'Chapter content downloaded. (index={chapter_dto.index}, title={chapter_dto.title})')

    logger.info(f'Download complete.')


@inject
def get_novel(
        id_or_url: str,
        novel_service: NovelService = Provide[Application.services.novel_service],
) -> Optional[Novel]:
    """retrieve novel is it exists in the database otherwise return none"""
    is_url = id_or_url.startswith("http")
    if is_url:
        novel = novel_service.get_novel_by_url(id_or_url)
    else:
        try:
            novel = novel_service.get_novel_by_id(int(id_or_url))
        except ValueError:
            logger.info(f'Value provided is neither a url or an id. (value={({id_or_url})})')
            sys.exit(1)

    if not novel:
        logger.info(f'Novel not found. ({"url" if is_url else "id"}={id_or_url})')

    return novel


@inject
def get_or_create_novel(
        id_or_url: str,
) -> Novel:
    """retrieve specified novel from database or web-crawl and create the novel"""
    novel = get_novel(id_or_url)

    if novel is None:
        if not id_or_url.startswith("http"):
            sys.exit(1)

        novel = create_novel(id_or_url)

    return novel
