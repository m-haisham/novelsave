from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("novelsave")
except PackageNotFoundError:
    import re
    from pathlib import Path

    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    with pyproject.open("r") as f:
        text = f.read()

    __version__ = re.search(r'version = "(.+?)"', text).group(1)

__source__ = "https://github.com/mHaisham/novelsave"
