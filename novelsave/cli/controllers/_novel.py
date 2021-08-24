import sys
from pathlib import Path

from dependency_injector.wiring import inject, Provide
from loguru import logger

from novelsave.cli import helpers as cli_helpers
from novelsave.containers import Application
from novelsave.core.services import BaseNovelService, BasePathService
from novelsave.core.services.source import BaseSourceGatewayProvider
from novelsave.exceptions import MetaDataSourceNotFoundException


@inject
def delete_downloaded_content(
        id_or_url: str,
        novel_service: BaseNovelService = Provide[Application.services.novel_service],
):
    """deletes all the downloaded content from chapters of novel"""
    try:
        novel = cli_helpers.get_novel(id_or_url)
    except ValueError:
        sys.exit(1)

    novel_service.delete_content(novel)
    logger.info(f"Deleted chapter content from novel (id={novel.id}, title='{novel.title}').")


@inject
def delete_associations(
        id_or_url: str,
        novel_service: BaseNovelService = Provide[Application.services.novel_service],
        path_service: BasePathService = Provide[Application.services.path_service],
):
    """Removes all except vital information related to novel, this includes chapters, metadata, and assets."""
    try:
        novel = cli_helpers.get_novel(id_or_url)
    except ValueError:
        sys.exit(1)

    novel_service.delete_volumes(novel)
    logger.info(f"Deleted volumes and chapters of novel (id={novel.id}, title='{novel.title}').")

    novel_service.delete_metadata(novel)
    logger.info(f"Deleted metadata of novel (id={novel.id}, title='{novel.title}').")

    if novel.thumbnail_path:
        path_service.resolve_data_path(Path(novel.thumbnail_path)).unlink(missing_ok=True)
        logger.info(f"Deleted thumbnail of novel (id={novel.id}, title='{novel.title}').")
    else:
        logger.info(f"Skipped deleting thumbnail of novel "
                    f"(id={novel.id}, title='{novel.title}', reason='Does not exist').")


def clean_novel(id_or_url: str, content_only: bool):
    """Remove accessory fields from novel

    Removes all except vital information related to novel, this includes chapters, metadata, and assets.

    If content_only flag is specified, only the chapter content is deleted, keeping the chapter entries as is.
    """
    if content_only:
        delete_downloaded_content(id_or_url)
    else:
        delete_associations(id_or_url)


@inject
def delete_novel(
        id_or_url: str,
        novel_service: BaseNovelService = Provide[Application.services.novel_service],
        path_service: BasePathService = Provide[Application.services.path_service],
):
    """delete all records of novel. this includes chapters, and assets"""
    try:
        novel = cli_helpers.get_novel(id_or_url)
    except ValueError:
        sys.exit(1)

    novel_service.delete_novel(novel)
    path_service.novel_save_path(novel)
    logger.info(f"Deleted novel (id={novel.id}, title='{novel.title}')")


@inject
def import_metadata(
        id_or_url: str,
        metadata_url: str,
        novel_service: BaseNovelService = Provide[Application.services.novel_service],
):
    """import metadata from a metadata supplied into an existing novel"""
    try:
        novel = cli_helpers.get_novel(id_or_url)
    except ValueError:
        sys.exit(1)

    meta_source_gateway = cli_helpers.get_meta_source_gateway(metadata_url)
    metadata_dtos = meta_source_gateway.metadata_by_url(metadata_url)

    novel_service.update_metadata(novel, metadata_dtos)
