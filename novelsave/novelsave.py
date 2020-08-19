import inspect

from .sources import Webnovel
from .sourcesave import SourceNovelSave
from .template import NovelSaveTemplate
from .websave import WebNovelSave


class NovelSave:
    def __new__(cls, *args, **kwargs):
        url = args[0] if args else kwargs['url']

        arguments = kwargs.copy()
        for i, arg in enumerate(inspect.getfullargspec(NovelSaveTemplate.__init__).args[1:]):
            try:
                arguments[arg] = args[i]
            except IndexError:
                if arg not in arguments.keys():
                    arguments[arg] = None

        if Webnovel.of(url):
            cls = WebNovelSave(arguments['url'], arguments['username'], arguments['password'])
        else:
            cls = SourceNovelSave(arguments['url'])

        return cls
