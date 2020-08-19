from novelsave import NovelSave

NOVEL = 'https://www.wuxiaworld.co/Reincarnation-Of-The-Strongest-Sword-God/'
CHAPTER = 'https://www.wuxiaworld.co/Reincarnation-Of-The-Strongest-Sword-God/1239956.html'

if __name__ == '__main__':

    novelsave = NovelSave(NOVEL)
    novelsave.create_epub()

    print()
    # novelsave = SourceNovelSave(NOVEL)
    # novelsave.download()
