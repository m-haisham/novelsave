from novelsave.sources import WuxiaWorldCo

NOVEL = 'https://www.wuxiaworld.co/Reincarnation-Of-The-Strongest-Sword-God/'
CHAPTER = 'https://www.wuxiaworld.co/Reincarnation-Of-The-Strongest-Sword-God/1239956.html'

if __name__ == '__main__':

    source = WuxiaWorldCo()
    print(WuxiaWorldCo.of(NOVEL))
    novel, chapters = source.novel(NOVEL)

    chapter = source.chapter(CHAPTER)
    print(chapter.paragraphs)

    print('')
