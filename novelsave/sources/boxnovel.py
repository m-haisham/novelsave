from typing import Tuple, List

from .source import Source
from ..models import Chapter, Novel


class BoxNovel(Source):
    base = 'https://boxnovel.com'

    @staticmethod
    def of(url: str) -> bool:
        return url[:len(BoxNovel.base)] == BoxNovel.base

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        novel = Novel(
            title=soup.find('div', {'class': 'post-title'}).text.strip(),
            author=soup.find('div', {'class': 'author-content'}).text,
            synopsis=soup.find('div', {'class': 'j_synopsis'}).text,
            thumbnail=soup.find('div', {'class': 'summary_image'}).find('img')['src'],
            url=url
        )

        chapters = []
        for element in soup.find_all('li', {'class': 'wp-manga-chapter'}):
            title_element = element.find('a')

            no, title = self._parse_title(title_element.text.strip())

            chapter = Chapter(
                no=no,
                title=title,
                url=title_element['href']
            )

            chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        # box novel displays chapter with two very different html layouts
        if soup.find('div', {'class': 'cha-content'}) is not None:
            full_title = soup.find('div', {'class': 'cha-tit'}).find('h3').text.strip()
            no, title = self._parse_chapter_title(full_title)

            paragraphs = [
                element.find('p').text.strip()
                for element in soup.find_all('div', {'class': 'cha-paragraph'})
            ]
        else:
            reading_content = soup.find('div', {'class': 'reading-content'})

            full_title = reading_content.find('h2').text
            no, title = self._parse_chapter_title(full_title)

            paragraphs = [
                element.text.strip()
                for element in reading_content.find_all('p')
            ]

        return Chapter(
            no=no,
            title=title,
            paragraphs=paragraphs,
            url=url
        )

    def _parse_title(self, s) -> Tuple[int, str]:
        if ' - ' in s:
            # there is a name in title
            order, title = s.split(' - ', maxsplit=1)
            no = int(order.split(' ', maxsplit=1)[-1])

        else:
            # no title, just chapter no
            title = s
            no = int(s.split(' ', maxsplit=1)[-1])

        return no, title

    def _parse_chapter_title(self, s) -> Tuple[int, str]:
        order, title = s.split(': ', maxsplit=1)
        no = int(order.split(' ')[-1])

        return no, title
