from typing import List

from .calibre_packager import CalibrePackager


class PdfPackager(CalibrePackager):

    def keywords(self) -> List[str]:
        return ['pdf']

    @property
    def args(self) -> List[str]:
        return [
            '--paper-size', 'letter',
            '--pdf-hyphenate',
            '--pdf-header-template',
            '<span style="color:#555; font-size:0.8em; font-weight:bold;">_TITLE_ &mdash; _SECTION_</span>',
            '--pdf-footer-template',
            '<div style="color:#555; font-size:0.8em; font-weight:bold;">_PAGENUM_</div>',
        ]

    @property
    def ext(self) -> str:
        return '.pdf'
