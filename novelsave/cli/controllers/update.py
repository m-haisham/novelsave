import sys

from loguru import logger

from ..helpers import get_novel, create_novel


def update(
        id_or_url: str,
        skip_chapters: bool,
):
    """
    update the novel metadata and downloads any new chapters if not specified otherwise

    if url is provided and novel does not exist, a new novel entry will be created.
    however if id is provided the process will be terminated

    :param id_or_url: id or url of the novel
    :param skip_chapters: whether to skip updating chapters
    :return: None
    """
    novel = get_novel(id_or_url)
    if novel is None:
        is_url = id_or_url.startswith('https')
        if not is_url:
            sys.exit(1)

        create_novel(id_or_url)
        return


