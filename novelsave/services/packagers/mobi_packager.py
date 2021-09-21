from functools import lru_cache
from pathlib import Path
from typing import List

from novelsave.core.entities.novel import Novel
from novelsave.core.services import BaseCalibreService, BasePathService
from novelsave.core.services.packagers import BasePackager


class MobiPackager(BasePackager):
    def __init__(
            self,
            calibre_service: BaseCalibreService,
            path_service: BasePathService,
    ):
        self.path_service = path_service
        self.calibre_service = calibre_service

    @property
    def priority(self):
        return 2

    def keywords(self) -> List[str]:
        return ['mobi']

    def package(self, novel: Novel) -> Path:
        output_file = self.destination(novel)
        input_file = output_file.parent / f'{output_file.parent.name}.epub'

        args = [
            '--book-producer', 'novelsave',
            '--unsmarten-punctuation',
            '--no-chapters-in-toc',
            '--enable-heuristics',
            '--disable-renumber-headings',
        ]

        try:
            self.calibre_service.ebook_convert(input_file, output_file, args)
        except FileNotFoundError:
            raise FileNotFoundError("Epub file not found. Mobi file is converted from the generated epub file. "
                                    "Make sure epub book variant exists.")

        return output_file

    @lru_cache(maxsize=1)
    def destination(self, novel: Novel):
        path = self.path_service.novel_save_path(novel)
        return path / f'{path.name}.mobi'
