from webnovel.bot import BASE_URL


class Scraper:
    @staticmethod
    def novel_url(novel_id):
        return f'{BASE_URL}/book/{novel_id}'

    @staticmethod
    def chapter_url(novel_id, chapter_id):
        return f'{BASE_URL}/book/{novel_id}/{chapter_id}'
