# NovelSave

[![GitHub version](https://badge.fury.io/gh/mHaisham%2Fnovelsave.svg)](https://badge.fury.io/gh/mHaisham%2Fnovelsave) [![PyPI version](https://badge.fury.io/py/novelsave.svg)](https://badge.fury.io/py/novelsave) 

Tool to convert novels to epub

## Install

```
pip install novelsave
```

or

```
pip install git+https://github.com/mHaisham/novelsave.git
```

## Commandline

### Example

**Update a novel**

```
novelsave https://www.webnovel.com/book/my-disciples-are-all-villains_16984011906162405 -u -p -c
```

**Check/Update configurations**

```
novelsave config
```

```
novelsave config -d novels
```

#### Save directory

Novels are saved to folder `novels` in user home

### Help

```batch
usage: __main__.py [-h] [-u] [-p] [-c] [--meta META] [--force-cover] [--force-create] [--force-meta] [--email EMAIL] [-v] [--threads THREADS] [--timeout TIMEOUT]
                   [--limit LIMIT] [-d DIR]
                   action

tool to convert novels to epub

positional arguments:
  action             novel url for downloading novels; 'config' to change configurations

optional arguments:
  -h, --help         show this help message and exit
  -v, --verbose      enable animations; only in pending
  --threads THREADS  number of download threads
  --timeout TIMEOUT  webdriver timeout
  --limit LIMIT      amount of chapters to download

actions:
  -u, --update       update novel details
  -p, --pending      download pending chapters
  -c, --create       create epub from downloaded chapters
  --meta META        metadata source url
  --remove-meta      remove current metadata
  --force-cover      download and overwrite the existing cover
  --force-create     force create epub
  --force-meta       force update metadata

credentials:
  --email EMAIL      webnovel email

config:
  -d DIR, --dir DIR  directory for saving novels
```

## Manual

Pass a url to the `NovelSave` class which will select the correct source for it.

```python
from novelsave import NovelSave

if __name__ == '__main__':
    save = NovelSave(url)
```

### Methods

`NovelSave` has 4 methods

- ```update(self, force_cover=False):```
- ```metadata(self, url, force=False):```
- ```download(self, thread_count=4, limit=None):```
- ```create_epub(self, force=False):```

### Database

you can access the database by using the `db` attribute of `NovelSave`

```python
    save.db
```

## Sources

- [webnovel.com](https://www.webnovel.com)
- [wuxiaworld.co](https://www.wuxiaworld.co)
- [boxnovel.com](https://www.boxnovel.co)
- [readlightnovel.org](https://www.readlightnovel.org)
- [insanitycave.poetry](https://insanitycave.poetry.blog)
- [ktlchamber.wordpress](https://ktlchamber.wordpress.com)
- [kieshitl.wordpress](https://kieshitl.wordpress.com)
- [scribblehub.com](https://www.scribblehub.com)
- [mtlnovel.com](https://www.mtlnovel.com)
- [fanfiction.net](https://www.fanfiction.net)
- [novelfull.com](https://novelfull.com)
- [wuxiaworld.com](https://www.wuxiaworld.com)
- [royalroad.com](https://www.royalroad.com)
- [forums.spacebattles.com](https://forums.spacebattles.com/)

## Metadata Sources

- [wlnupdates.com](https://www.wlnupdates.com)
- [novelupdates.com](https://www.novelupdates.com)