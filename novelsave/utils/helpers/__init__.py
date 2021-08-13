from typing import Iterable, Tuple


def unzip_arguments(args: tuple, kwargs: dict, pairs: Iterable[Tuple[int, str]]):
    """
    This is a helper function used extract to arguments from :args and :kwargs
    """
    unzipped = []
    for pair in pairs:
        try:
            unzipped.append(args[pair[0]])
        except IndexError:
            unzipped.append(kwargs[pair[1]])

    return unzipped
