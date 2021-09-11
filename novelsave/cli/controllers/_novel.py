import shutil
import sys

from dependency_injector.wiring import inject, Provide
from loguru import logger

from novelsave.cli import helpers as cli_helpers
from novelsave.containers import Application
from novelsave.core.services import BaseNovelService, BasePathService, BaseAssetService
from novelsave.core.services.source import BaseSourceService
from novelsave.exceptions import SourceNotFoundException


@inject
def show_info(
        id_or_url: str,
        novel_service: BaseNovelService = Provide[Application.services.novel_service],
):
    """print current information of novel"""
    try:
        novel = cli_helpers.get_novel(id_or_url, silent=True)
    except ValueError:
        sys.exit(1)

    logger.info('[novel]')
    logger.info(f'id = {novel.id}')
    logger.info(f'title = {novel.title}')
    logger.info(f'author = {novel.author}')
    logger.info(f'lang = {novel.lang}')
    logger.info(f'thumbnail = {novel.thumbnail_url}')
    logger.info(f'synopsis = ')
    for line in novel.synopsis.splitlines():
        logger.info(f'{"":<4}{line.strip()}')

    logger.info(f'urls = ')
    for n_url in novel_service.get_urls(novel):
        logger.info(f'{"":<4}{n_url.url}')

    logger.info('')
    logger.info('[chapters]')
    chapters = novel_service.get_chapters(novel)
    logger.info(f'total = {len(chapters)}')
    logger.info(f'downloaded = {len([c for c in chapters if c.content])}')


@inject
def list_novels(
        novel_service: BaseNovelService = Provide[Application.services.novel_service],
        source_service: BaseSourceService = Provide[Application.services.source_service],
):
    novels = novel_service.get_all_novels()
    for novel in novels:
        url = novel_service.get_primary_url(novel)

        try:
            source = source_service.source_from_url(url).name
        except SourceNotFoundException:
            source = None

        logger.info(f"Novel (id={novel.id}, title='{novel.title}', {source=}, last_updated='{novel.last_updated}').")


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
        asset_service: BaseAssetService = Provide[Application.services.asset_service],
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

    asset_service.delete_assets_of_novel(novel)
    logger.info(f"Deleted asset entries of novel (id={novel.id}, title='{novel.title}').")

    novel_dir = path_service.novel_data_path(novel)
    if novel_dir.exists():
        shutil.rmtree(novel_dir)
    logger.info(f"Deleted data of novel (path='{path_service.resolve_data_path(novel_dir)}')")


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

    novel_dir = path_service.novel_data_path(novel)
    if novel_dir.exists():
        shutil.rmtree(novel_dir)
    logger.info(f"Deleted data of novel (path='{path_service.resolve_data_path(novel_dir)}')")

    novel_service.delete_novel(novel)
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
