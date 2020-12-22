from typing import List

from .metasource import MetaSource
from ..models import MetaData


class NovelUpdates(MetaSource):
    base = 'https://www.novelupdates.com'

    @staticmethod
    def of(value):
        return value.startswith(NovelUpdates.base)

    def retrieve(self, url) -> List[MetaData]:
        metadata = []
        soup = self.soup(url)

        # alternate titles
        for text in soup.select_one('#editassociated').find_all(text=True, recursive=False):
            metadata.append(MetaData('title', text.strip(), {'type': 'alternate'}))

        # novel type
        metadata.append(MetaData('type', soup.select_one('.genre.type').text))

        # genre
        for a in soup.select('#seriesgenre > a'):
            metadata.append(MetaData('subject', a.text))

        # og language
        metadata.append(MetaData('lang', soup.select_one('#showlang > a').text, {'id': 'original language'}))

        # illustrators
        for a in soup.select('#showartists > a'):
            metadata.append(MetaData('contributor', a.text, {'role': 'ill'}))

        # publishers
        if soup.select_one('#showopublisher > a'):
            metadata.append(MetaData('publisher', soup.select_one('#showopublisher > a').text, {'role': 'original'}))
        if soup.select_one('#showepublisher > a'):
            metadata.append(MetaData('publisher', soup.select_one('#showepublisher > a').text, {'role': 'english'}))

        # publication
        if not soup.select_one('#edityear > .seriesna'):
            metadata.append(MetaData('date', soup.select_one('#edityear').text.strip(), {'role': 'publication'}))

        return metadata
