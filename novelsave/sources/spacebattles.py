from typing import List, Tuple
from urllib.parse import urlparse

from .source import Source
from ..exceptions import ResponseException
from ..models import Chapter, Novel


class Spacebattles(Source):
    base = 'https://forums.spacebattles.com'

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        threadmarks_url = f'{url.rstrip("/")}/threadmarks'
        soup = self.soup(threadmarks_url)

        author_element = soup.select_one('.username')

        # getting a thumbnail
        stripped_baseurl = self.base.rstrip("/")

        # getting writer profile image
        try:
            author_soup = self.soup(f'{stripped_baseurl}{author_element["href"]}')
            avatar = author_soup.select_one('.avatarWrapper > .avatar')
            thumbnail = f'{stripped_baseurl}{avatar["href"]}'
        except ResponseException as e:
            # access to profile denied
            if e.response.status_code == 403:
                thumbnail = None

        novel = Novel(
            title=soup.select_one('.p-breadcrumbs > li:last-child').text.strip(),
            author=author_element.text,
            thumbnail=thumbnail,
            url=url,
        )

        chapters = []
        for i, a in enumerate(soup.select('.block-body--threadmarkBody.is-active > div > div > div:first-child a')):
            chapter = Chapter(
                index=i,
                title=a.text,
                url=f'{stripped_baseurl}{a["href"]}'
            )

            chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        parsed_url = urlparse(url)
        raw_url = f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}'

        soup = self.cached_soup(raw_url)

        article = soup.select_one(f'.u-anchorTarget#{parsed_url.fragment}').parent
        content = article.select_one('.message-inner .message-userContent .bbWrapper')

        content.attrs = {}
        paragraphs = str(content)[5:-6].split('<br/>\n<br/>')
        paragraphs = [p.strip() for p in paragraphs]

        return Chapter(
            title=article.select_one('.message-cell--threadmark-header > span').text.strip(),
            paragraphs='<p>' + '</p><p>'.join(paragraphs) + '</p>',
            url=url,
        )