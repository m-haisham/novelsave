import sys

from .. import helpers


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
    novel = helpers.get_novel(id_or_url)
    if novel is None:
        is_url = id_or_url.startswith('https')
        if not is_url:
            sys.exit(1)

        novel = helpers.create_novel(id_or_url)
    else:
        helpers.update_novel(novel)

    helpers.download_thumbnail(novel)

    if limit is None or limit > 0:
        helpers.download_pending(novel, limit)
