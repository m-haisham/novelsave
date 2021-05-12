from typing import List, Tuple

import requests
from bs4 import BeautifulSoup

from .source import Source
from ...models import Chapter, Novel


class NovelsRock(Source):
    base = 'https://novelsrock.com'

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        novel = Novel(
            title=soup.select_one('.breadcrumb > li:last-child').text.strip(),
            author=', '.join([a.text.strip() for a in soup.select('.author-content > a')]),
            thumbnail=soup.select_one('.summary_image img')['src'],
            synopsis='\n'.join([p.text.strip() for p in soup.select('.summary__content')]),
            url=url,
        )

        for a in soup.select('.summary_content_wrap a[href*="genre"]'):
            novel.add_meta('subject', a.text.strip())

        novel_id = soup.select_one('.wp-manga-action-button[data-action=bookmark]')['data-post']

        response = requests.post('https://novelsrock.com/wp-admin/admin-ajax.php', data={
            'action': 'manga_get_chapters',
            'manga': int(novel_id)
        })

        soup = BeautifulSoup(response.content, 'lxml')

        chapters = []
        for a in reversed(soup.select('.wp-manga-chapter > a')):
            chapter = Chapter(
                index=len(chapters),
                title=a.text.strip(),
                url=a['href'],
            )

            chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        contents = soup.select('div.reading-content p')

        body = []
        for p in contents:
            for ad in p.select('h3, .code-block, .adsense-code'):
                ad.decompose()
            body.append(str(p))

        return Chapter(
            paragraphs=''.join(body),
            url=url,
        )
