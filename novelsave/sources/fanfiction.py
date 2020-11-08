from typing import List, Tuple
from urllib.parse import urlparse

from .source import Source
from ..models import Chapter, Novel
from ..tools import StringTools


class Fanfiction(Source):
    base = 'https://www.fanfiction.net/'

    @staticmethod
    def of(url: str) -> bool:
        return StringTools.startswith(url, Fanfiction.base)

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        cover = None
        image_element = soup.select_one('#profile_top img.cimage')
        if image_element:
            cover = f'https:{image_element["src"]}'

        novel = Novel(
            title=soup.select_one('#profile_top b.xcontrast_txt, #content b').text.strip(),
            author=soup.select_one('#profile_top, #content').select_one('a[href*="/u/"]').text.strip(),
            thumbnail=cover,
            url=url,
        )

        id = urlparse(url).path.split('/')[2]

        chapters = []
        chapter_select = soup.select_one('#chap_select, select#jump')
        if chapter_select:
            # multi chapter fan-fictions
            for i, option in enumerate(chapter_select.select('option')):
                chapter = Chapter(
                    index=i,
                    title=option.text.strip(),
                    url=f'https://www.fanfiction.net/s/{id}/{option["value"]}'
                )

                chapters.append(chapter)
        else:
            # single chapter fan-fictions
            chapters.append(
                Chapter(
                    index=0,
                    title=novel.title,
                    url=url,
                )
            )

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        chapter_select = soup.select_one('#chap_select, select#jump')
        if chapter_select:
            title = chapter_select.find('option', selected=True).text.strip()
        else:
            title = soup.select_one('#profile_top b.xcontrast_txt, #content b').text.strip()

        return Chapter(
            title=title,
            paragraphs=str(soup.select_one('#storytext, #storycontent')),
            url=url,
        )

