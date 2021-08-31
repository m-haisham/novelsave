import requests

from novelsave import __version__
from novelsave.core.services import BaseMetaService


class MetaService(BaseMetaService):

    @property
    def current_version(self) -> str:
        return __version__

    def get_latest_version(self) -> str:
        response = requests.get('https://pypi.org/pypi/novelsave/json')
        if not response.ok:
            raise ConnectionError(f"Response received was not valid: GET {response.url} {response.status_code}")

        data = response.json()
        versions = sorted((v for v in data['releases'].keys() if 'a' not in v), reverse=True)
        return versions[0]
