import sys

from dependency_injector.wiring import inject, Provide
from loguru import logger

from novelsave.cli.helpers import get_novel
from novelsave.containers import Application
from novelsave.core.services import BaseNovelService


@inject
def remove_url(
        url: str,
        novel_service: BaseNovelService = Provide[Application.services.novel_service],
):
    """Removes the selected url from the database"""
    try:
        novel = get_novel(url)
    except ValueError:
        sys.exit(1)

    try:
        novel_service.remove_url(novel, url)
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    else:
        logger.info(f"Removed url from novel (id={novel.id}, title='{novel.title}', {url=}).")


@inject
def add_url(
        id_or_url: str,
        new_url: str,
        novel_service: BaseNovelService = Provide[Application.services.novel_service],
):
    """Deletes the novel and all its data"""
    try:
        novel = get_novel(id_or_url)
    except ValueError:
        sys.exit(1)

    try:
        novel_service.add_url(novel, new_url.rstrip('/'))
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    else:
        logger.info(f"Url added to novel (id={novel.id}, title='{novel.title}', {new_url=}).")
