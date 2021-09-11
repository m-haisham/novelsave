import re


def slugify(s: str, replace=''):
    """Remove special characters that will prevent string from being used as file name

    It is important that 'replace' is not a special character.
    Preferably one of '', ' ', '_', or '-'.

    >>> slugify('Hansel&Gretel', replace='-')
    'Hansel-Gretel'

    :param s: String to convert to strip
    :param replace: Character to replace the special characters with
    :returns: String slug that may be safely used as a filename or url part
    """
    return re.sub(r'[\\/:*"\'<>|.%$^&£?]', replace, s)


def format_bytes(size: int) -> str:
    """
    scale and label the size of bytes.

    >>> format_bytes(1580)
    '1.54 Kb'

    >>> format_bytes(512)
    '512.00 b'

    barely modified version of https://stackoverflow.com/a/49361727/11728401
    """
    # 2**10 = 1024
    power = 2 ** 10
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1

    return f'{size:.2f} {power_labels[n]}b'
