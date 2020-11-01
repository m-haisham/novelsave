# NovelSave

Tool to convert novels to epub

## Install

```
pip install novelsave
```

## Commandline

### Example
```
python3 -m novelsave https://www.webnovel.com/book/my-disciples-are-all-villains_16984011906162405 -u -p -c
```

#### Save directory

Novels are saved to folder `novels` in user home

### Help

```batch
usage: __main__.py [-h] [-tc THREADS] [-t TIMEOUT] [-u] [-p] [-c] [--email EMAIL] novel

tool to convert novels to epub

positional arguments:
  novel                 either id (only for webnovels) or url of novel

optional arguments:
  -h, --help            show this help message and exit
  -tc THREADS, --threads THREADS
                        number of download threads
  -to TIMEOUT, --timeout TIMEOUT
                        webdriver timeout

actions:
  -u, --update          update novel details
  -p, --pending         download pending chapters
  -c, --create          create epub from downloaded chapters

credentials:
  --email EMAIL         webnovel email

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