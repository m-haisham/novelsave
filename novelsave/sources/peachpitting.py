from typing import List, Tuple

from .source import Source
from ..models import Chapter, Novel


class PeachPitting(Source):
    base = 'https://peachpitting.com'

    bad_tags = [
        'noscript', 'script', 'iframe', 'form', 'img', 'ins',
        'button', 'input', 'amp-auto-ads', 'pirate', 'ul'
    ]

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        details_parent, synopsis_parent, *_ = soup.select('.elementor-text-editor')

        author = None
        subjects = []
        for p in details_parent.select('p'):
            text = p.text.strip()
            if text.startswith('Author: '):
                author = text.strip('Author: ')
            elif text.startswith('Tags: '):
                subjects = [s.strip() for s in text.strip('Tags: ').split(',')]

        synopsis = '\n'.join([p.text.strip() for p in synopsis_parent.select('p')])

        novel = Novel(
            title=soup.select_one('h3.elementor-heading-title').text.strip(),
            thumbnail=soup.select_one('.elementor-image img')['src'],
            synopsis=synopsis,
            author=author,
            url=url,
        )

        # tags
        for subject in subjects:
            novel.add_meta('subject', subject)

        # other contributors
        for a in soup.select('.pp-multiple-authors-wrapper .author'):
            novel.add_meta('contributor', a.text.strip())

        chapters = []
        for a in soup.select('.pt-cv-page > div a'):
            chapter = Chapter(
                index=len(chapters),
                title=a.text.strip(),
                url=a['href'],
            )

            chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        content = soup.select_one('#wtr-content')

        # remove ads
        for div in content.select('.ad-section'):
            div.extract()

        self.clean_contents(content)

        return Chapter(
            title=soup.select_one('.post-title').text.strip(),
            paragraphs=str(content),
            url=url,
        )
