import re
from typing import Tuple, List

import requests

from .source import Source
from ...models import Novel, Chapter


class NovelFun(Source):
    base = 'https://novelfun.net'
    graphql = f'{base}/graphql'

    query = """query chapters_NovelRefetchQuery(
    $slug: String!
    $startChapNum: Int
) {...chapters_list_items} fragment chapters_list_items on Query {
    chapterListChunks(
        bookSlug: $slug,
        chunkSize: %d,
        startChapNum: $startChapNum
    ) {
        items {
            title
            chapNum
            url
        }
    }
}
"""

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        novel = Novel(
            title=soup.select_one('h1').text.strip(),
            author=soup.select_one('a[href*="author"]').text.strip(),
            synopsis='\n'.join([p.text.strip() for p in soup.select('article > div > p')]),
            url=url,
        )

        novel.thumbnail = soup.select_one(f'img[title="{novel.title}"]')['src']

        for a in soup.select('td a[href*="genre"]'):
            novel.add_meta('subject', a.text.strip())

        title_slug = url.rstrip('/').split('/')[-1]
        total = int(re.match(r'(\d+)', soup.select_one('h2 ~ div').text).group(1))
        data = {
            'id': 'chapters_NovelRefetchQuery',
            'query': self.query % total,
            'variables': {
                'slug': title_slug,
                'startChapNum': 1,
            },
        }
        response = requests.get(self.graphql, json=data)

        chapters = [
            Chapter(
                index=c['chapNum'],
                title=c["title"],
                url=self.base+c['url'],
            )
            for c in response.json()['data']['chapterListChunks'][0]['items']
        ]

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        content = soup.select_one('h1 ~ div')
        self.clean_contents(content)

        return Chapter(
            paragraphs=str(content),
            url=url,
        )