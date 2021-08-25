import re


def slugify(s, replace=''):
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
