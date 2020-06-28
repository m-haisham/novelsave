from novelsave import NovelSave

from temp import CHRYSALIS_ID

if __name__ == '__main__':
    novelsave = NovelSave(CHRYSALIS_ID)
    # novelsave.update_data()
    # novelsave.download_pending()
    novelsave.create_epub()