import re
from typing import Tuple, List

from .source import Source
from ..models import Novel, Chapter


class WuxiaCo(Source):
    base = 'https://www.wuxiaworld.co'
    url_pattern = re.compile(r'https://www\.wuxiaworld\.co(?!(m))')

    @staticmethod
    def of(url: str) -> bool:
        return bool(WuxiaCo.url_pattern.match(url))

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        novel = Novel(
            title=soup.find('div', {'class': 'book-name'}).text,
            author=soup.find('div', {'class': 'author'}).find('span', {'class': 'name'}).text,
            synopsis=soup.find('div', {'class': 'synopsis'}).find('p').text,
            thumbnail=soup.find('div', {'class': 'book-img'}).find('img')['src'],
            url=url
        )

        chapters = []
        for i, item in enumerate(soup.find_all('a', {'class': 'chapter-item'})):
            no, title = self._parse_title(item.find('p').text)

            chapter = Chapter(
                index=i,
                no=int(no),
                title=title,
                url=f"{self.base}{item['href']}"
            )

            chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        no, title = self._parse_title(soup.find('h1', {'class': 'chapter-title'}).text)

        # remove google ads
        for element in soup.find_all('ins', {'class': 'adsbygoogle'}):
            element.decompose()

        content = [
            text.strip()
            for text in soup.find('div', {'class': 'chapter-entity'}).find_all(text=True, recursive=False)
        ]

        # removes random junk inside paragraphs
        # including new-line, tab
        #
        content = self._clean_content(content)

        return Chapter(
            no=int(no),
            title=title,
            paragraphs=content,
            url=url
        )

    def _parse_title(self, u_title: str) -> Tuple[int, str]:
        # when title is affixed by chapter
        if u_title[:8].lower() == 'chapter ':
            _, no, title = u_title.split(' ', maxsplit=2)

            try:
                # Chapter {no} {title}
                return int(no), title
            except ValueError:
                # semi colon after no
                # Chapter {no}: {title}
                return int(no[:-1]), title

        try:
            # {no} {title}
            no, title = u_title.split(' ', maxsplit=1)
            return int(no), title
        except ValueError:
            # typically volume 0 chapters that doesnt have chapter no.
            # {title}
            return -1, u_title

    def _clean_content(self, content):
        paragraphs = []

        # check is paragraph has line breaks or tabs inside
        # if split to separate paragraphs
        for i, para in enumerate(content):
            para = re.sub(r'[\n\t\r]', ' ', para)

            parts = [part.strip() for part in para.split('  ') if part]

            # filter out junk lines
            p = ' '.join((
                part
                for part in parts
                if part not in ['Please go to', 'to read the latest chapters for free']
            ))

            paragraphs.append(p)

        return paragraphs
