import re
from typing import List, Tuple

from .source import Source
from ..models import Chapter, Novel


class Chrysanthemumgarden(Source):
    base = 'https://chrysanthemumgarden.com/'

    bad_tags = [
        'div', 'pirate', 'script',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    ]

    blacklist_patterns = [
        r'^[\W\D]*(volume|chapter)[\W\D]+\d+[\W\D]*$',
        r'^(\s| )+$',  # non-breaking whitespace
    ]

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        synopsis = ''
        synopsis_elements = soup.select('.entry-content > p, hr')
        for element in synopsis_elements:
            if element.tag == 'hr':
                break

            synopsis += element.text.strip() + '\n'

        novel = Novel(
            title=soup.select_one('.novel-title').find(text=True).strip(),
            author=soup.select_one('.author-name > a').text.strip(),
            synopsis=synopsis.strip(),
            thumbnail=soup.select_one('.novel-cover img')['src'],
            url=url,
        )

        for a in soup.select('.series-tag'):
            novel.add_meta('subject', a.text.strip())

        chapters = []
        for i, a in enumerate(soup.select('.chapter-item > a')):
            chapter = Chapter(
                index=i,
                title=a.text.strip(),
                url=a['href'],
            )

            chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        content = soup.select_one('#novel-content')
        self.clean_contents(content)

        # initial cleaning process can leave empty paragraphs as a side effect
        for element in content.find_all():
            if not element.text.strip():
                element.extract()

        return Chapter(
            title=soup.select_one('.chapter-title').text.strip(),
            paragraphs=str(content),
            url=url,
        )

    def clean_element(self, element):

        # this removes hidden elements
        try:
            style = element['style']
            if re.match(r'(height:\s*1px|width:\s*0)', style, flags=re.IGNORECASE):
                element.extract()
                return
        except KeyError:
            pass

        if 'class' in element.attrs and 'jum' in element['class']:
            self.reorder_text(element)

        super(Chrysanthemumgarden, self).clean_element(element)

    def reorder_text(self, element):
        text = ''
        for char in element.text:
            try:
                text += self.jumble_map[char]
            except KeyError:
                text += char

        element.string = text

    jumble_map = {'j': 'a', 'y': 'b', 'm': 'c', 'v': 'd', 'f': 'e', 'o': 'f', 'u': 'g', 't': 'h', 'l': 'i', 'p': 'j',
                  'x': 'k', 'i': 'l', 'w': 'm', 'c': 'n', 'b': 'o', 'q': 'p', 'd': 'q', 'g': 'r', 'r': 's', 'a': 't',
                  'e': 'u', 'n': 'v', 'k': 'w', 'z': 'x', 's': 'y', 'h': 'z', 'C': 'A', 'D': 'B', 'J': 'C', 'G': 'D',
                  'S': 'E', 'M': 'F', 'X': 'G', 'L': 'H', 'P': 'I', 'A': 'J', 'B': 'K', 'O': 'L', 'Z': 'M', 'R': 'N',
                  'Y': 'O', 'U': 'P', 'H': 'Q', 'E': 'R', 'V': 'S', 'K': 'T', 'F': 'U', 'N': 'V', 'Q': 'W', 'W': 'X',
                  'T': 'Y', 'I': 'Z'}
