from typing import List, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .source import Source
from ..models import Chapter, Novel

class DragonTea(Source):
    base = 'https://dragontea.ink/'

    @staticmethod
    def of(url: str) -> bool:
        return url.startswith(DragonTea.base)

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        summary_paragraphs = [p.text for p in soup.select('.summary__content > p')]

        novel = Novel(
            title=soup.select_one('.post-title').text.strip(),
            author=soup.select_one('.author-content').text.strip(),
            thumbnail=soup.select_one('.summary_image img')['src'],
            synopsis='\n'.join(summary_paragraphs),
            url=url,
        )

        # other metadata
        for item in soup.select('.post-content_item'):
            if item.select_one('.summary-heading').text.strip() == 'Alternative':
                novel.add_meta('title', item.select_one('.summary-content').text.strip(), others={'role': 'alt'})
                break

        for a in soup.select('.genres-content > a'):
            novel.add_meta('subject', a.text.strip())

        artist_content = soup.select_one('.artist-content > a')
        if artist_content:
            novel.add_meta('contributor', artist_content.text.strip(), others={'link': artist_content['href']})

        novel_id = soup.select_one('.rating-post-id')['value']
        response = self.session.post(
            'https://dragontea.ink/wp-admin/admin-ajax.php',
            data={
                'action': 'manga_get_chapters',
                'manga': novel_id,
            }
        )

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
    
        content = soup.select_one('.reading-content')

        # text-left has a better collection of paragraphs...
        # however we are not taking any chances assuming its always there
        text_left = content.select_one('.text-left')
        if text_left:
            content = text_left

        self.clean_contents(content)

        return Chapter(
            title=soup.select_one('.breadcrumb >li.active').text.strip(),
            paragraphs=str(content),
            url=url,
        )
