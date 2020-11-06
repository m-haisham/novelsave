from io import BytesIO

import requests

from ..ui import Loader


class UiTools:

    @staticmethod
    def download(url, desc=None, chunksize=1024):
        """
        :return: downloaded bytes
        """
        bytes = BytesIO()

        desc = desc or f'downloading {url}'
        with Loader(desc=desc) as brush:
            response = requests.get(url, stream=True)

            total_length = response.headers.get('content-length')
            if total_length is None:  # no content length header
                bytes.write(response.content)
            else:
                total_length = int(total_length)

                # start download stream
                brush.value = 0
                brush.total = total_length

                for data in response.iter_content(chunk_size=chunksize):
                    brush.value += bytes.write(data)
                    brush.desc = f'[{brush.value}/{brush.total}] {desc}'

                # hide bytes
                brush.desc = desc

        return bytes

    @staticmethod
    def print_success(*args):
        print('[✓]', *args)

    @staticmethod
    def print_error(*args):
        print('[✗]', *args)

    @staticmethod
    def print_var(name, value):
        print(f'[-] {name} = {value}')

    @staticmethod
    def print_info(*args):
        print('[-]', *args)
