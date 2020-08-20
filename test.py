from novelsave import NovelSave

NOVEL = 'https://www.wuxiaworld.co/Reincarnation-Of-The-Strongest-Sword-God/'
CHAPTER = 'https://www.wuxiaworld.co/Reincarnation-Of-The-Strongest-Sword-God/1239956.html'

WEBNOVEL = 'https://www.webnovel.com/book/absolute-great-teacher_16989846406186505'

if __name__ == '__main__':

    novelsave = NovelSave(WEBNOVEL)
    novelsave.download()

    print()
    # novelsave = SourceNovelSave(NOVEL)
    # novelsave.download()
