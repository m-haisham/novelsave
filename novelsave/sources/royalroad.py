from typing import Tuple, List

from .source import Source
from ..models import Novel, Chapter


class RoyalRoad(Source):
    base = 'https://www.royalroad.com'

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        novel = Novel(
            title=soup.find("h1", {"property": "name"}).text.strip(),
            thumbnail=soup.find("img", {"class": "img-offset thumbnail inline-block"})['src'],
            author=soup.find("span", {"property": "name"}).text.strip(),
            url=url,
        )

        chapters = []
        for a in soup.find('tbody').findAll('a', href=True):
            chapter = Chapter(
                index=len(chapters),
                title=a.text.strip(),
                url=f'{self.base}{a["href"]}'
            )

            chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        contents = soup.select_one('.chapter-content')
        self.clean_contents(contents)

        return Chapter(
            title=soup.find('h1').text.strip(),
            paragraphs=str(contents),
            url=url,
        )
