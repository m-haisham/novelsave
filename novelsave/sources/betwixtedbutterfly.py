from typing import List, Tuple

from bs4 import BeautifulSoup

from .source import Source
from ..models import Chapter, Novel
from ..exceptions import ChapterException


class BetwixtedButterfly(Source):
    base = 'https://betwixtedbutterfly.com'

    bad_tags = [
        'noscript', 'script', 'iframe', 'form', 'img', 'ins',
        'button', 'input', 'amp-auto-ads', 'pirate',
        'nav', 'h1', 'h2',
    ]

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        soup = self.soup(url)

        details_parent, synopsis_parent, *_ = soup.select('.elementor-text-editor')

        author = None
        for p in details_parent.select('p'):
            if p.text.startswith('Author: '):
                author = p.text.strip('Author: ')
                break

        synopsis = '\n'.join([p.text.strip() for p in synopsis_parent.select('p')])

        novel = Novel(
            title=soup.select_one('h2.elementor-heading-title').text.strip(),
            thumbnail=soup.select_one('.elementor-image img')['src'],
            author=author,
            synopsis=synopsis,
            url=url,
        )

        # tags
        for a in soup.select('a.elementor-button'):
            novel.add_meta('subject', a.text.strip())

        chapters = []
        for a in soup.select('.elementor-tab-content > p a'):
            chapter = Chapter(
                index=len(chapters),
                title=a.text.strip(),
                url=a['href']
            )

            chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        soup = self.soup(url)

        elements = soup.select(".entry-inner section .elementor-element:not(.elementor-widget-button, "
                               ".elementor-column)")
        if elements:
            content = BeautifulSoup(f'<div>{"".join([str(element) for element in elements])}</div>', 'lxml').select_one('div')
        else:
            content = soup.select_one('.entry-inner')

        # this source lists chapters that aren't completed/translated in table of contents
        # links of said chapter are redirected to another url that indicates the lack of the chapter
        if content is None:
            raise ChapterException('Absent', f'"{url}" redirected to placeholder')

        # remove navigation buttons
        for button in content.select('.elementor-widget-button'):
            button.extract()

        # wp-block-columns -> navigation
        # code-block -> ads
        for div in content.select('.wp-block-columns, .code-block'):
            div.extract()

        self.clean_contents(content)

        return Chapter(
            paragraphs=str(content),
            url=url,
        )
