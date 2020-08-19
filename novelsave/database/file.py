import re


def slugify(s):
    return re.sub(r'[\\/:*"\'<>|.%$^&£?]', '', s)