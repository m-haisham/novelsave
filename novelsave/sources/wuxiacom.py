from typing import List, Tuple

from .source import Source
from ..models import Chapter, Novel


class WuxiaCom(Source):
    base = 'https://www.wuxiaworld.com'

    blacklist_patterns = [
        r'^<span>(...|\u2026)</span>$',
        r'^translat(ed by|or)',
        r'(volume|chapter) .?\d+',
    ]

    @staticmethod
    def of(url: str) -> bool:
        return url.startswith(WuxiaCom.base)

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        try:
            thumbnail = soup.select_one('img.media-object')['src']
        except Exception:
            thumbnail = None

        authors = ''
        for d in soup.select_one('.media-body dl, .novel-body').select('dt, dd'):
            authors += d.text.strip()
            authors += ' ' if d.name == 'dt' else '; '

        novel = Novel(
            title=soup.select_one('.section-content h2').text,
            thumbnail=thumbnail,
            author=authors.strip().strip(';'),
            url=url,
        )

        chapters = []
        for panel in soup.select('#accordion .panel-default'):
            for a in panel.select('ul.list-chapters li.chapter-item a'):
                chapter = Chapter(
                    index=len(chapters),
                    url=f"{self.base}{a['href']}"
                )

                chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        contents = soup.select_one('#chapterContent')
        if not contents:
            contents = soup.select_one('#chapter-content')
        if not contents:
            contents = soup.select_one('.panel-default .fr-view')
        if not contents:
            raise ValueError(f'Unable to read chapter content from {url}')

        for nav in (contents.select('.chapter-nav') or []):
            nav.extract()

        self.clean_contents(contents)

        return Chapter(
            title=soup.select_one('#chapter-outer  h4').text.strip(),
            paragraphs=str(contents),
            url=url,
        )
