from typing import List, Tuple

from .source import Source
from ..models import Chapter, Novel


class NovelFull(Source):
    base = 'https://novelfull.com'

    blacklist_patterns = [
        r'^\s*Translator:',
        r'^\s*Editor:',
        r'^\s*Atlas Studios',
        r'Read more chapter on NovelFull',
        r'full thich ung',
        r'If you find any errors \( broken links.*let us know < report chapter >',
    ]

    @staticmethod
    def of(url: str) -> bool:
        return url.startswith(NovelFull.base)

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        image_element = soup.select_one('.info-holder .book img')

        author = ''
        for a in soup.select('.info-holder .info a'):
            if a['href'].startswith('/author/'):
                author = a.text.strip()

        novel = Novel(
            title=image_element['alt'],
            thumbnail=self.base + image_element['src'],
            author=author,
            url=url,
        )

        last_pagination = soup.select_one('#list-chapter .pagination .last a')
        page_count = int(
            last_pagination['data-page']) if last_pagination else 0

        chapters = []
        for page in range(1, page_count + 2):
            for chapter in self.parse_chapter_list(url, page):
                chapter.index = len(chapters)
                chapters.append(chapter)

        return novel, chapters

    def parse_chapter_list(self, novel_url, page):
        url = f'{novel_url.rstrip("/")}?page={page}&per-page=50'
        soup = self.soup(url)

        chapters = []
        for a in soup.select('ul.list-chapter li a'):
            chapter = Chapter(
                title=a['title'].strip(),
                url=self.base + a['href'],
            )

            chapters.append(chapter)

        return chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        content = soup.select_one('div#chapter-content')

        self.clean_contents(content)
        for ads in content.select('h3, h2, .adsbygoogle, script, ins, .ads, .ads-holder'):
            ads.extract()

        return Chapter(
            title=soup.select_one('.chapter-text').find(text=True, recursive=False).strip(),
            paragraphs=str(content),
            url=url,
        )
