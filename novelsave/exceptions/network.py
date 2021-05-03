from requests import Response


class ResponseException(Exception):
    def __init__(self, response, *args):
        super(ResponseException, self).__init__(*args)
        self.response: Response = response

    @property
    def message(self):
        message = f'''The website responded with status code: {self.response.status_code}.
{self.response.url}

'''
        if self.response.status_code == 404:
            message += 'The provided url cannot be reached. Make sure the novel is accessible.'

        return message
