from webnovel import WebnovelBot
from webnovel.bot import BASE_URL


class Scraper:
    def __init__(self, email=None, password=None, timeout=20):
        self.bot = WebnovelBot(timeout=timeout)

        if email is not None and password is not None:
            self.bot.driver.get(BASE_URL)
            self.bot.signin(email, password)

        # method exposing
        self.novel = self.bot.novel
        self.close = self.bot.close
        self.create_api = self.bot.create_api

    @staticmethod
    def novel_url(novel_id):
        return f'{BASE_URL}/book/{novel_id}'

    @staticmethod
    def chapter_url(novel_id, chapter_id):
        return f'{BASE_URL}/book/{novel_id}/{chapter_id}'
