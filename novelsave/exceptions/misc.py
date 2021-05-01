
class DownloadLimitException(ValueError):
    def __init__(self, limit: int):
        super(DownloadLimitException, self).__init__()
        self.limit = limit

    def __str__(self):
        return f'''Provided download limit ({self.limit}) is invalid. Download limit must be a positive integer.
    (use "--limit 1..." to limit download to a specific amount)
    (omit argument to download all pending chapters)'''
