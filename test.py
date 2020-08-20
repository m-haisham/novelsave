from novelsave import NovelSave
from novelsave.concurrent import ConcurrentActions

NOVEL = 'https://www.wuxiaworld.co/Reincarnation-Of-The-Strongest-Sword-God/'
CHAPTER = 'https://www.wuxiaworld.co/Reincarnation-Of-The-Strongest-Sword-God/1239956.html'

if __name__ == '__main__':

    def task(i):
        return i * 2

    ca_manager = ConcurrentActions(4, task=task)

    for i in range(10):
        ca_manager.add(i)

    ca_manager.start()
    while not ca_manager.done:
        print(ca_manager.queue_out.get())