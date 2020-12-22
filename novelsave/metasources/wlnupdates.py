from typing import List

import requests

from .metasource import MetaSource
from ..models import MetaData


class WlnUpdates(MetaSource):
    base = 'https://www.wlnupdates.com/'
    api_endpoint = 'https://www.wlnupdates.com/api'

    @staticmethod
    def of(value):
        return value.startswith(WlnUpdates.base)

    def retrieve(self, url) -> List[MetaData]:
        metadata = []
        
        # get json data
        id = int(url.split('/')[4])
        data = self.api_request(id, 'get-series-id')['data']

        # alternate names
        for name in data['alternatenames']:
            if name == data['title']:
                continue

            metadata.append(MetaData('title', name, others={'type': 'alternate'}))

        # illustrators
        for obj in data['illustrators']:
            metadata.append(MetaData('contributor', obj['illustrator'], others={'role': 'ill'}))

        # publishers
        for obj in data['publishers']:
            metadata.append(MetaData('publisher', obj['publisher']))

        # genre
        for obj in data['genres']:
            metadata.append(MetaData('subject', obj['genre']))

        # tags [tags are not needed]
        # for obj in data['tags']:
        #     metadata.append(MetaData('tag', obj['tag']))

        # original language
        if data['orig_lang']:
            metadata.append(MetaData('lang', data['orig_lang'], others={'id': 'original language'}))

        # publication
        if data['pub_date']:
            metadata.append(MetaData('date', data['pub_date'], others={'role': 'publication'}))

        return metadata

    def api_request(self, id: int, mode: str):
        response = requests.post(self.api_endpoint, json={'id': id, 'mode': mode})
        return self._verify_response(response).json()
