from ..main import cli
from ... import __version__


@cli.command(name='version')
def _version():
    """Show application version"""

    # Using print here instead of logger because, we want the version
    # as plain possible, also there is no point in printing this
    # to a log file
    print(__version__)
