import re
from typing import List, Tuple

from .source import Source
from ...models import Chapter, Novel

class NovelHall(Source):
    base = 'https://www.novelhall.com'

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        synopsis_element = soup.select_one('.js-close-wrap')
        synopsis_element.select_one('span').extract()

        novel = Novel(
            title=soup.select_one('.book-info h1').text.strip(),
            thumbnail=soup.select_one('.img-thumbnail')['src'],
            synopsis=synopsis_element.text.strip(),
            url=url,
        )

        for span in soup.select('.booktag span.blue'):
            for text in span.find_all(text=True, recursive=False):
                _text = str(text).strip()
                if _text.startswith('Author：'):
                    novel.author = _text.lstrip('Author：')
                    break

        for a in soup.select('.booktag a[href*="genre"]'):
            novel.add_meta('subject', a.text.strip())

        chapters = []
        for i, a in enumerate(soup.select('#morelist > ul li a')):
            chapter = Chapter(
                index=i,
                title=a.text.strip(),
                url=self.base+a['href'],
            )

            chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        content = soup.select_one('.entry-content')
        self.clean_contents(content)

        content = '<p>' + re.sub(r'<br ?/?>', '</p><p>', str(content).strip('<div></div>').strip()) + '</p>'

        return Chapter(
            title=soup.select_one('.single-header h1').text.strip(),
            paragraphs=content,
            url=url,
        )
