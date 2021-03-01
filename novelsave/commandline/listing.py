import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..database import NovelData, UserConfig
from ..exceptions import MissingSource
from ..sources import parse_source
from ..ui import ConsolePrinter, PrinterPrefix as Prefix


class NovelListing:
    def __init__(self, verbose=True):
        self.user = UserConfig()
        self.console = ConsolePrinter(verbose)

    def show_all(self):
        sources = self._get_sources()

        for key in sources.keys():

            # print the source title
            self.console.print(f'{key} ({len(sources[key])})')
            for data in sources[key]:
                # prints minimal novel information
                novel = data.novel.parse()
                self.console.raw_print(f"'{novel.title}' by {novel.author}")
                self.console.list(novel.url)

            self.console.endline()

    def show_novel(self, url):
        data, path = self._open(url)
        if data is None:
            return

        # print basic information about novel
        novel = data.novel.parse()
        self.console.print('Information')
        self.console.list('title:', novel.title)
        self.console.list('by:', novel.author)
        self.console.list('synopsis:', novel.synopsis)
        self.console.list('thumbnail:', novel.thumbnail)
        self.console.list('lang:', novel.lang)
        self.console.list('url:', novel.url)
        self.console.endline()

        # print metadata information about novel
        metadata = data.metadata.all()
        self.console.print(f'Metadata ({len(metadata)})')
        if self.console.verbose:
            for m in metadata:

                # build others to a more readable format
                others = ' '.join([f'[{key}={value}]' for key, value in m['others'].items()])
                if others:
                    others = ' ' + others

                self.console.list(f"{m['name']}: {m['value']}{others}")
        self.console.endline()

        # print chapters of the novel
        chapters = data.chapters.all()
        self.console.print(f'Chapters ({len(chapters)})')
        if self.console.verbose:
            for c in chapters:
                self.console.list(c.title)
        self.console.endline()

    def reset_novel(self, url, full=True):
        data, path = self._open(url, load=False)
        if data is None:
            return

        # display a minimal number of information
        novel = data.novel.parse()
        self.console.print(f'{"Delete" if full else "Reset"} \'{novel.title}\'')
        self.console.list(f'by {novel.author}')
        self.console.list(novel.url)
        self.console.endline()

        confirm = self.console.confirm('Are you sure?')
        if not confirm:
            self.console.print('Cancelled')
            return

        try:
            if full:
                # database has to be closed before we delete the files associated with it
                # lest it throw an OSError
                data.close()

                # remove everything
                shutil.rmtree(path)
            else:
                # remove chapters
                shutil.rmtree(data.chapters.path)

                # remove metadata
                data.metadata.truncate()
        except PermissionError as e:
            self.console.print(e, prefix=Prefix.ERROR)

    def _get_sources(self) -> Dict[str, List[NovelData]]:
        novels = {}

        novels_path = Path(self.user.directory.get())
        for source in novels_path.iterdir():
            if not source.is_dir():
                continue

            novels[source.name] = []
            for novel in source.iterdir():
                data = NovelData(novel, load_chapters=False)

                # novel is assumed to exist only if url is not None
                if data.novel.get('url') is not None:
                    novels[source.name].append(data)

        return novels

    def _open(self, url: str, load=True) -> Tuple[Optional[NovelData], Optional[Path]]:
        try:
            source = parse_source(url)
        except MissingSource:
            self.console.print(f"'{url}' could not be assigned to any supported source\n", prefix=Prefix.ERROR)
            self.console.endline()
            return None, None

        try:
            path = self.user.directory.get() / Path(source.source_folder_name()) / source.novel_folder_name(url)
            data = NovelData(path, create=False, load_chapters=load)
        except FileNotFoundError:
            self.console.print('Record of novel does not exist\n', prefix=Prefix.ERROR)
            return None, None

        return data, path
