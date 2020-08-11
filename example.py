from novelsave import NovelSave

# replace these values
NOVEL = 6831850602000905
EMAIL = None
PASSWORD = None

if __name__ == '__main__':
    ns = NovelSave(NOVEL)
    ns.email = EMAIL
    ns.password = PASSWORD

    # ns.update_data()
    ns.download_pending()
    # ns.create_epub()