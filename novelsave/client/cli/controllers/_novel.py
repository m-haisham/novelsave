import json
import shutil
import sys
from typing import Literal

from dependency_injector.wiring import inject, Provide
from loguru import logger
from tabulate import tabulate

from novelsave.client.cli import helpers as cli_helpers
from novelsave.containers import Application
from novelsave.core.services import BaseNovelService, BasePathService, BaseAssetService
from novelsave.core.services.source import BaseSourceService
from novelsave.exceptions import SourceNotFoundException, NSError


@inject
def show_info(
    id_or_url: str,
    fmt: Literal["default", "json"] = "default",
    novel_service: BaseNovelService = Provide[Application.services.novel_service],
):
    """print current information of novel"""
    try:
        novel = cli_helpers.get_novel(id_or_url, silent=True)
    except ValueError:
        sys.exit(1)

    chapters = novel_service.get_chapters(novel)

    data = {
        "novel": {
            "id": novel.id,
            "title": novel.title,
            "author": novel.author,
            "lang": novel.lang,
            "thumbnail": novel.thumbnail_url,
            "synopsis": novel.synopsis.splitlines(),
            "urls": [o.url for o in novel_service.get_urls(novel)],
        },
        "chapters": {
            "total": len(chapters),
            "downloaded": len([c for c in chapters if c.content]),
        },
    }

    if fmt is None or fmt == "default":
        endl = "\n"
        text = "[novel]" + endl

        def format_keyvalue(key, value):
            text = f"{key} = "

            if type(value) == str:
                text += f"'{value}'"
            else:
                text += str(value)

            text += endl
            return text

        for key, value in data["novel"].items():
            text += format_keyvalue(key, value)

        text += endl
        text += "[chapters]" + endl

        for key, value in data["chapters"].items():
            text += format_keyvalue(key, value)

    elif fmt == "json":
        text = json.dumps(data, indent=4)
    else:
        raise NSError(f"Provided novel information formatter is not supported: {fmt}.")

    for line in text.splitlines():
        logger.info(line)


@inject
def list_novels(
    novel_service: BaseNovelService = Provide[Application.services.novel_service],
    source_service: BaseSourceService = Provide[Application.services.source_service],
):
    novels = novel_service.get_all_novels()

    table = [["Id", "Title", "Source", "Last updated"]]

    for novel in novels:
        url = novel_service.get_primary_url(novel)

        try:
            source = source_service.source_from_url(url).name
        except SourceNotFoundException:
            source = None

        table.append([novel.id, novel.title, source, novel.last_updated])

    for line in tabulate(table, headers="firstrow", tablefmt="github").splitlines():
        logger.info(line)


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
    logger.info(f"Deleted chapter content from '{novel.title}' ({novel.id}).")


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

    logger.info(f"Removing associated data from '{novel.title}' ({novel.id})…")

    novel_service.delete_volumes(novel)
    logger.info("Deleted volumes and chapters of novel.")

    novel_service.delete_metadata(novel)
    logger.info("Deleted metadata of novel.")

    asset_service.delete_assets_of_novel(novel)
    logger.info("Deleted asset entries of novel.")

    novel_dir = path_service.novel_data_path(novel)
    if novel_dir.exists():
        shutil.rmtree(novel_dir)
    logger.info(
        f"Deleted saved file data of novel: {{data.dir}}/{path_service.relative_to_data_dir(novel_dir)}."
    )


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

    logger.info(f"Deleting '{novel.title}' ({novel.id})…")

    novel_dir = path_service.novel_data_path(novel)
    if novel_dir.exists():
        shutil.rmtree(novel_dir)
    logger.info(
        f"Deleted data of novel: {{data.dir}}/{path_service.relative_to_data_dir(novel_dir)}."
    )

    novel_service.delete_novel(novel)
    logger.info("Deleted novel entry.")


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
