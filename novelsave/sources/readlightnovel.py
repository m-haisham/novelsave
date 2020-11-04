import unicodedata
from typing import Tuple, List

from .source import Source
from ..models import Novel, Chapter
from ..tools import StringTools


class ReadLightNovel(Source):
    base = 'https://www.readlightnovel.org'

    @staticmethod
    def of(url: str) -> bool:
        return url[:len(ReadLightNovel.base)] == ReadLightNovel.base

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        # parse author
        author = None
        for element in soup.find('div', {'class': 'novel-left'}).find_all('div', {'class': 'novel-detail-item'}):
            if element.find('div', {'class': 'novel-detail-header'}).text.strip() == 'Author(s)':
                author = element.find('div', {'class': 'novel-detail-body'}).find('li').text.strip()
                break

        novel = Novel(
            title=soup.find('div', {'class': 'block-title'}).text.strip(),
            author=author,
            synopsis=soup
                .find('div', {'class': 'novel-right'})
                .find('div', {'class': 'novel-detail-item'})
                .find('div', {'class': 'novel-detail-body'})
                .text,
            thumbnail=soup.find('div', {'class': 'novel-cover'}).find('img')['src'],
            url=url
        )

        chapters = []
        for i, element in enumerate(
                soup.find('div', {'class': 'tab-content'}).find_all('ul', {'class': 'chapter-chs'})
        ):
            children = list(element.find_all('a'))
            if not children:
                continue

            offset = len(children) * i
            for j, link in enumerate(children):
                text = link.text
                trail = text.split(' ', maxsplit=2)[1]

                # readlightnovel has a weird chapter link that doesnt point to anywhere
                # and a repeat of the last chapter
                if trail == '' or '.end' in trail:
                    continue

                chapter = Chapter(
                    index=offset + j,
                    no=int(trail),
                    title=text.strip(),
                    url=link['href']
                )

                chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        content = soup.find('div', {'class': 'chapter-content3'}).find('div', {'class': 'desc'})

        title_element = content.find('h3')
        if title_element is not None:
            # those that have and actual title

            # title can have some unicode characters in them
            text = unicodedata.normalize("NFKD", title_element.text)
            order, title = text.split(': ', maxsplit=1)

            no = int(order.split(' ', maxsplit=2)[1])
        else:
            title = no = None
            for text in reversed(content.find_all(text=True, recursive=False, limit=20)):
                text = text.strip()
                if text[:8] == 'Chapter ':
                    if ': ' in text:
                        text, title = text.split(': ', maxsplit=1)
                    else:
                        title = text

                    order = text.split(' ', maxsplit=1)[-1]
                    if title == order:
                        title = f'Chapter {order}'
                    if '(END)' in order:
                        order = order.split(' ', maxsplit=1)[0]

                    no = int(order)
                    break

        # paragraphs
        paragraphs = []

        def add_paragraph(s: str):
            if s and not StringTools.startswith(s, 'Translator:') and not StringTools.startswith(s, 'Chapter '):

                paragraphs.append(
                    self.format_paragraph(s)
                )

        if content.find('p') is None:
            # no <p> elements
            for text in content.find_all(text=True, recursive=False):
                add_paragraph(text.strip())
        else:
            para_elements = content.find_all('p', recursive=False)
            for element in para_elements:
                text = element.text.strip()
                add_paragraph(text)

        return Chapter(
            no=no,
            title=title,
            paragraphs=paragraphs,
            url=url
        )

    def format_paragraph(self, p: str):

        construct = list(p)
        indexes = []
        for i, c in enumerate(construct):
            if c == '.':
                if construct[i-1] == ' ':
                    indexes.append(i-1)

                try:
                    if construct[i+1] == ' ' and not construct[i+2]:
                        indexes.append(i+1)
                except IndexError:
                    pass

        # no need for changes
        if len(indexes) == 0:
            return p

        paragraph = ''
        for i, c in enumerate(construct):
            if i not in indexes:
                paragraph += c

        return paragraph