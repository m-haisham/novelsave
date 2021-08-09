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
    """retrieve information about the novel from webpage and insert novel into database"""
    source_service = source_provider.source_from_url(url)
    novel_dto, chapter_dtos, metadata_dtos = source_service.novel_by_url(url)

    return novel_service.insert_novel(novel_dto)


@inject
def get_or_create_novel(
        id_or_url: Union[int, str],
        novel_service: NovelService = Provide[Application.services.novel_service],
) -> Novel:
    """retrieve specified novel from database or web-crawl and create the novel"""
    is_url = id_or_url.startswith("http")
    if is_url:
        novel = novel_service.get_novel_by_url(id_or_url)
    else:
        novel = novel_service.get_novel_by_id(id_or_url)

    # novel was retrieved successfully from database
    if novel:
        return novel

    if not is_url:
        logger.error(f"Novel ({id_or_url}) not found")
        sys.exit(1)

    return create_novel(id_or_url)
