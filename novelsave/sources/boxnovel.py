import re
from typing import Tuple, List

from .source import Source
from ..models import Chapter, Novel
from ..tools import StringTools


class BoxNovel(Source):
    base = 'https://boxnovel.com/'

    @staticmethod
    def of(url: str) -> bool:
        return StringTools.startswith(url, BoxNovel.base)

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        description = soup.find('div', {'class': 'j_synopsis'})
        if description is None:
            description = soup.find('div', {'id': 'editdescription'})

        novel = Novel(
            title=''.join(soup.find('div', {'class': 'post-title'}).find('h3').find_all(text=True, recursive=False)).strip(),
            author=soup.find('div', {'class': 'author-content'}).text,
            synopsis=description.text,
            thumbnail=soup.find('div', {'class': 'summary_image'}).find('img')['src'],
            url=url
        )

        chapters = []
        chapter_elements = soup.find_all('li', {'class': 'wp-manga-chapter'})
        for i, element in enumerate(reversed(chapter_elements)):
            title_element = element.find('a')

            no, title = self._parse_title(title_element.text.strip())

            chapter = Chapter(
                index=i,
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

            p_elements = soup.find_all('div', {'class': 'cha-paragraph'})
            if p_elements:

                paragraphs = []
                for element in p_elements:
                    p = element.find('p')
                    if p is not None:
                        paragraphs.append(p.text.strip())

                # paragraphs = [
                #     element.find('p').text.strip()
                #     for element in p_elements
                # ]
            else:
                paragraphs = []
                for element in soup.find('div', {'class': 'cha-content'}).find_all('p'):
                    if element.find('em') is not None:
                        paragraphs.append(element.find('em').text.strip())
                    else:
                        paragraphs.append(str(element.find(text=True, recursive=False)).strip())

        else:
            reading_content = soup.find('div', {'class': 'reading-content'})

            full_title = None
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
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
            paragraphs=[para for para in paragraphs if para],
            url=url
        )

    def _parse_title(self, s) -> Tuple[float, str]:
        if ' - ' in s:
            # there is a name in title
            order, title = s.split(' - ', maxsplit=1)
            no = float(order.split(' ', maxsplit=1)[-1])

        else:
            # no title, just chapter no
            title = s
            no = float(s.split(' ', maxsplit=1)[-1])

        return no, title

    def _parse_chapter_title(self, s) -> Tuple[int, str]:
        match = re.match(r'Chapter (\d+):? ?(.+)', s, re.IGNORECASE)
        return float(match.group(1)), match.group(2).strip()
