import sys
from typing import Optional

from loguru import logger

from .. import helpers
from ...utils.helpers import string_helper


def update(
        id_or_url: str,
        browser: Optional[str] = None,
        limit: int = -1,
):
    """
    update the novel metadata and downloads any new chapters if not specified otherwise

    if url is provided and novel does not exist, a new novel entry will be created.
    however if id is provided the process will be terminated

    :param id_or_url: id or url of the novel
    :param browser: extract cookies from this browser
    :param limit: no. of chapters to update
    :return: None
    """
    try:
        novel = helpers.get_novel(id_or_url)
    except ValueError:
        is_url = string_helper.is_url(id_or_url)
        if not is_url:
            sys.exit(1)

        logger.info(f"Attempting to create new novel entry using url.")
        novel = helpers.create_novel(id_or_url, browser)
    else:
        helpers.update_novel(novel, browser)

    helpers.download_thumbnail(novel)

    if limit is None or limit > 0:
        helpers.download_pending(novel, limit)
