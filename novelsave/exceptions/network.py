from requests import Response


class ResponseException(Exception):
    def __init__(self, response, *args):
        super(ResponseException, self).__init__(*args)
        self.response: Response = response
