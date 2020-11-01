# NovelSave

Tool to convert novels to epub

## Install

```
pip install novelsave
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
usage: __main__.py [-h] [-u] [-p] [-c] [--force-cover] [--email EMAIL] [--threads THREADS] [--timeout TIMEOUT] [--limit LIMIT] [-d DIR] action

tool to convert novels to epub

positional arguments:
  action             novel url for downloading novels; 'config' to change configurations

optional arguments:
  -h, --help         show this help message and exit
  --threads THREADS  number of download threads
  --timeout TIMEOUT  webdriver timeout
  --limit LIMIT      amount of chapters to download

actions:
  -u, --update       update novel details
  -p, --pending      download pending chapters
  -c, --create       create epub from downloaded chapters
  --force-cover      download and overwrite the existing cover

credentials:
  --email EMAIL      webnovel email

config:
  -d DIR, --dir DIR  directory for saving novels
```

## Manual

Access all the saved data using `novelsave.database.NovelData`

Manipulate the data using the accessors provided in the class

Creating an epub is easy as calling a function. `novelsave.Epub().create()`

## Sources

- [webnovel.com](https://www.webnovel.com/)
- [wuxiaworld.co](https://www.wuxiaworld.co/)
- [boxnovel.com](https://www.boxnovel.co/)
- [readlightnovel.org](https://www.readlightnovel.org/)
- [insanitycave.poetry](https://insanitycave.poetry.blog/)
- [ktlchamber.wordpress](https://ktlchamber.wordpress.com)
- [kieshitl.wordpress](https://kieshitl.wordpress.com)