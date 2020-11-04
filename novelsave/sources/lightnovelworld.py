import re
from typing import Tuple, List

from .source import Source
from ..models import Novel, Chapter
from ..tools import StringTools


class LightNovelWorld(Source):
    base = 'https://www.lightnovelworld.com'

    chapter_title_regex = re.compile(r'chapter (\d+\.?\d*):? ?(.+)?', flags=re.IGNORECASE)

    @staticmethod
    def of(url: str) -> bool:
        return StringTools.startswith(url, LightNovelWorld.base)

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        novel = Novel(
            title=soup.find('h1', {'class': 'novel-title'}).text,
            author=soup.find('div', {'class': 'author'}).find('a').text.strip(),
            thumbnail=soup.find('figure', {'class': 'cover'}).find('img')['src'],
            url=url,
        )

        chapters = []
        for i, li in enumerate(soup.find('ul', {'class': 'chapter-list'}).children):
            a = li.find('a')

            chapter = Chapter(
                index=i,
                no=int(float(li['data-chapterno'])),
                url=f"{LightNovelWorld.base}{a['href']}"
            )

            chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        title_element = soup.find('div', {'class': 'titles'}).find('h2')
        result = self.chapter_title_regex.search(title_element.text)
        if len(result.groups()) > 1:
            title = result.group(2)
        else:
            title = title_element.text.strip()

        chapter = Chapter(
            no=int(float(result.group(1))),
            title=title,
            paragraphs=[],
            url=url,
        )

        chapter_content = soup.find('div', {'class': 'chapter-content'})
        for text in chapter_content.find_all(text=True):
            chapter.paragraphs.append(text.strip())

        return chapter
