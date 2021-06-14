from typing import List, Tuple

from .source import Source
from ...models import Chapter, Novel

class NovelGate(Source):
    base = 'https://novelgate.net'

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        novel = Novel(
            title=soup.select_one('.film-info .name').text.strip(),
            author=soup.select_one('a[href*="author"]').text.strip(),
            thumbnail=soup.select_one('.film-info .book-cover')['data-original'],
            synopsis='\n'.join([p.text.strip() for p in soup.select('.film-content > p')]),
            url=url,
        )

        for a in soup.select('.film-info a[href*="genre"]'):
            novel.add_meta('subject', a.text.strip())

        chapters = []
        for i, div in enumerate(soup.select('#list-chapters > .book')):
            volume = (i, div.select_one('.title a').text.strip())

            for a in div.select('.list-chapters > li a'):
                chapter = Chapter(
                    index=len(chapters),
                    title=a.text.strip(),
                    volume=volume,
                    url=self.base + a['href'],
                )

                chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        contents = soup.select_one('#chapter-body')
        self.clean_contents(contents)

        return Chapter(
            paragraphs=str(contents),
            url=url,
        )