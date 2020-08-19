from novelsave.sources import WuxiaWorldCo
from novelsave.database import NovelBase


NOVEL = 'https://www.wuxiaworld.co/Reincarnation-Of-The-Strongest-Sword-God/'
CHAPTER = 'https://www.wuxiaworld.co/Reincarnation-Of-The-Strongest-Sword-God/1239956.html'

if __name__ == '__main__':
    source = WuxiaWorldCo()

    print('Opening database')
    db = NovelBase(NOVEL)

    print('downloading')
    novel, chapters = source.novel(NOVEL)

    print('setting')
    db.novel.set(novel)

    print()