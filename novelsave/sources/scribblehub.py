from typing import List, Tuple

import requests
from bs4 import BeautifulSoup

from .source import Source
from ..models import Chapter, Novel


class ScribbleHub(Source):
    base = 'https://www.scribblehub.com/'

    @staticmethod
    def of(url: str) -> bool:
        return url[:len(ScribbleHub.base)] == ScribbleHub.base

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        synopsis_paragraphs = [element.text for element in soup.find('div', {'class': 'wi_fic_desc'}).find_all('p')]

        novel = Novel(
            title=soup.find('div', {'class': 'fic_title'}).text.strip(),
            author=soup.find('span', {'class': 'auth_name_fic'}).text.strip(),
            synopsis='\n'.join(synopsis_paragraphs),
            thumbnail=soup.find('div', {'class': 'fic_image'}).find('img')['src'],
            url=url
        )

        id = int(url.split('/')[4])
        chapters = self.parse_toc(id)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        return Chapter(
            title=soup.select_one('.chapter-title').text.strip(),
            paragraphs=str(soup.select_one('#chp_raw')),
            url=url,
        )

    def parse_toc(self, id: int) -> List[Chapter]:

        response = requests.post(
            'https://www.scribblehub.com/wp-admin/admin-ajax.php',
            data={
                'action': 'wi_gettocchp',
                'strSID': id,
            },
        )

        soup = BeautifulSoup(response.content, 'lxml')
        chapter_elements = soup.find_all('li')

        chapters = []
        for i, element in enumerate(reversed(chapter_elements)):
            a = element.find('a')

            chapter = Chapter(
                index=i,
                title=a.text.strip(),
                url=a['href']
            )

            chapters.append(chapter)

        return chapters
