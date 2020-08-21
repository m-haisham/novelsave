import re
from typing import Tuple, List

from .source import Source
from ..models import Chapter, Novel
from ..tools import StringTools

class BoxNovel(Source):
    base = 'https://boxnovel.com'

    @staticmethod
    def of(url: str) -> bool:
        return url[:len(BoxNovel.base)] == BoxNovel.base

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        description = soup.find('div', {'class': 'j_synopsis'})
        if description is None:
            description = soup.find('div', {'id': 'editdescription'})

        novel = Novel(
            title=soup.find('div', {'class': 'post-title'}).text.strip(),
            author=soup.find('div', {'class': 'author-content'}).text,
            synopsis=description.text,
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

            full_title = None
            for tag in ['h2', 'h3']:
                elements = reading_content.find_all(tag)
                if elements:
                    full_title = ' '.join([element.text for element in elements])
                    break

            # if title is in <p>
            if full_title is None:
                full_title = reading_content.find('p').text

                # remove the title from it
                p_elements = reading_content.find_all('p')[1:]
            else:
                p_elements = reading_content.find_all('p')

            if full_title[0] != 'C':
                raise Exception(url)

            no, title = self._parse_chapter_title(full_title)

            paragraphs = [
                element.text.strip()
                for element in p_elements
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
        match = re.match(r'Chapter (\d+):? ?(.+)', s, re.IGNORECASE)
        return int(match.group(1)), match.group(2).strip()
