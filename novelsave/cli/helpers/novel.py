import sys
from typing import Union, Optional

from loguru import logger
from dependency_injector.wiring import inject, Provide

from novelsave.containers import Application
from novelsave.core.entities.novel import Novel
from novelsave.services import NovelService
from novelsave.services.source import SourceGatewayProvider


@inject
def create_novel(
        url: str,
        novel_service: NovelService = Provide[Application.services.novel_service],
        source_provider: SourceGatewayProvider = Provide[Application.services.source_gateway_provider],
) -> Novel:
    """
    retrieve information about the novel from webpage and insert novel into database.
    this includes chapter list and metadata.
    """
    source_gateway = source_provider.source_from_url(url)
    if source_gateway is None:
        logger.error(f'Could not find source corresponding to url, {url}')
        sys.exit(1)

    logger.info(f'Retrieving novel (url={url}) information')
    novel_dto, chapter_dtos, metadata_dtos = source_gateway.novel_by_url(url)

    novel = novel_service.insert_novel(novel_dto)
    novel_service.insert_chapters(novel, chapter_dtos)
    novel_service.insert_metadata(novel, metadata_dtos)

    logger.info(f'New novel (id={novel.id}, title={novel.title}, chapters={len(chapter_dtos)})')
    return novel


@inject
def get_novel(
        id_or_url: str,
        novel_service: NovelService = Provide[Application.services.novel_service],
):
    """retrieve novel is it exists in the database otherwise return none"""
    is_url = id_or_url.startswith("http")
    if is_url:
        novel = novel_service.get_novel_by_url(id_or_url)
    else:
        try:
            novel = novel_service.get_novel_by_id(int(id_or_url))
        except ValueError:
            logger.error(f'Value provided ({id_or_url}) is neither a url or an id.')
            sys.exit(1)

    if not novel:
        logger.error(f'Novel ({"url" if is_url else "id"}={id_or_url}) not found.')

    return novel


@inject
def get_or_create_novel(
        id_or_url: str,
) -> Novel:
    """retrieve specified novel from database or web-crawl and create the novel"""
    novel = get_novel(id_or_url)

    # novel was retrieved successfully from database
    if novel:
        return novel

    if not id_or_url.startswith("http"):
        sys.exit(1)

    return create_novel(id_or_url)
