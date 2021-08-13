import sys

from ..helpers import get_novel, create_novel, update_novel, download_pending


def update(
        id_or_url: str,
        limit: int = -1,
):
    """
    update the novel metadata and downloads any new chapters if not specified otherwise

    if url is provided and novel does not exist, a new novel entry will be created.
    however if id is provided the process will be terminated

    :param id_or_url: id or url of the novel
    :param limit: no. of chapters to update
    :return: None
    """
    novel = get_novel(id_or_url)
    if novel is None:
        is_url = id_or_url.startswith('https')
        if not is_url:
            sys.exit(1)

        novel = create_novel(id_or_url)
    else:
        update(novel)

    if limit is None or limit > 0:
        download_pending(novel, limit)
