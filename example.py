from novelsave import WebNovelSave

# replace these values
NOVEL = 6831850602000905
EMAIL = None
PASSWORD = None

if __name__ == '__main__':
    ns = WebNovelSave(NOVEL)
    ns.email = EMAIL
    ns.password = PASSWORD

    # ns.update_data()
    ns.download_pending()
    # ns.create_epub()
