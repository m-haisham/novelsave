import re
from typing import List, Tuple

from .source import Source
from ..models import Chapter, Novel


class WattPad(Source):
    base = 'https://www.wattpad.com'

    # 'https://my.w.tt', makes save novel folder naming weird

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        novel = Novel(
            title=soup.select('h1')[0].text.strip(),
            thumbnail=soup.select('div.cover.cover-lg img')[0]['src'],
            author=soup.select('div.author-info strong a')[0].text,
            synopsis=soup.select('h2.description')[0].text,
            url=url,
        )

        chapters = []
        for a in soup.select('ul.table-of-contents a'):
            chapter = Chapter(
                index=len(chapters),
                url=f'{self.base}{a["href"]}',
                title=a.text.strip() or f'Chapter {len(chapters)}'
            )

            chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        pages = int(re.search('[1-9]', re.search('("pages":)([1-9])', str(soup)).group(0)).group(0))
        contents = []
        for i in range(1, pages + 1):
            page_url = f'{url}/page/{i}'
            soup_page = self.soup(page_url)
            for p in soup_page.select('pre p'):
                contents.append(str(self.clean_contents(p)))

        return Chapter(
            title=(soup.select_one('.h2') or soup.select_one('h2')).text.strip(),
            paragraphs=''.join(contents),
            url=url,
        )
