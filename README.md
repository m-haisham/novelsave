# NovelSave

[![GitHub version](https://badge.fury.io/gh/mHaisham%2Fnovelsave.svg)](https://badge.fury.io/gh/mHaisham%2Fnovelsave) [![PyPI version](https://badge.fury.io/py/novelsave.svg)](https://badge.fury.io/py/novelsave)

Tool to convert novels to epub

> **v0.6.+ is not compatible with previous versions**

## Install

```
pip install novelsave
```

or

```
pip install git+https://github.com/mHaisham/novelsave.git
```

## Usage

### Update a novel

```bash
novelsave novel https://www.webnovel.com/book/my-disciples-are-all-villains_16984011906162405 -u -p -c
```

### Check/Update configurations

```bash
novelsave config
```

```bash
novelsave config -d novels
```

### Save directory

Novels are by default saved to folder `novels` in user home

## Help

### `novelsave --help`

```
usage: novelsave [-h] [-v] {novel,config,list} ...

tool to convert novels to epub

positional arguments:
  {novel,config,list}
    novel              download, update, and delete novels
    list               manipulate currently existing novels
    config             update and view user configurations

optional arguments:
  -h, --help           show this help message and exit
  -v, --verbose        extra information
```

### `novelsave novel --help`

```
usage: novelsave novel [-h] [-u] [-p] [-c] [--meta META] [--remove-meta] [--force-cover] [--force-create] [--force-meta] [--username USERNAME]
                       [--password PASSWORD] [--force-login] [--use-cookies USE_COOKIES] [--threads THREADS] [--timeout TIMEOUT] [--limit LIMIT]
                       url

positional arguments:
  url                   novel url or identifier for downloading novels

optional arguments:
  -h, --help            show this help message and exit
  --threads THREADS     number of download threads
  --timeout TIMEOUT     webdriver timeout
  --limit LIMIT         amount of chapters to download

actions:
  -u, --update          update novel details
  -p, --pending         download pending chapters
  -c, --create          create epub from downloaded chapters
  --meta META           metadata source url
  --remove-meta         remove current metadata
  --force-cover         download and overwrite the existing cover
  --force-create        force create epub
  --force-meta          force update metadata

auth:
  --username USERNAME   username or email field
  --password PASSWORD   password field; not recommended, refer to README for more details
  --force-login         remove existing cookies and login
  --use-cookies USE_COOKIES
                        use cookies from specified browser
```

### `novelsave list --help`

```
usage: novelsave list [-h] [--novel NOVEL] [--reset] [--full]

optional arguments:
  -h, --help     show this help message and exit
  --novel NOVEL  takes the url of the novel and displays meta information
  --reset        remove chapters and metadata. to be used with --novel
  --full         remove everything including compiled epub files. to be used with --reset
```

### `novelsave config --help`

```
usage: novelsave config [-h] [-d DIR]

optional arguments:
  -h, --help         show this help message and exit
  -d DIR, --dir DIR  directory for saving novels
```

## Login and cookies

Two methods of accessing authenticated content are provided

### Browser cookies

> Recommended method of access

Uses cookies from available browsers access content

use syntax `--use-cookies [browser]`. for example

```
novelsave novel https://www.webnovel.com/book/my-disciples-are-all-villains_16984011906162405 -u -p -c --use-cookies firefox
```

Requires to be Signed in, in the browser of choice

**Available**

`chrome` `firefox` `chromium` `opera` `edge`

### Login

Username and password are sent to the website server to authenticate.

Cookies are now persisted and stored at config's location.

Novelsave attempts to use the available cookies unless:

- any of the cookies from relevant domains are expired

- user provides the flag `--force-login`

refer to [sources](#sources) to check supported sites.

## Manual

Pass a url to the `NovelSave` class which will select the correct source for it.

```python
from novelsave import NovelSave

if __name__ == '__main__':
    save = NovelSave(url)
```

### Methods

`NovelSave` has 6 methods

- ```update(self, force_cover=False):```
- ```metadata(self, url, force=False):```
- ```remove_metadata(self, with_source=True):```
- ```download(self, thread_count=4, limit=None):```
- ```create_epub(self, force=False):```
- ```def login(self, cookie_browser: Union[str, None] = None, force=False):```

### Database

you can access the database by using the `db` attribute of `NovelSave`

```python
    save.db
```

## Sources

> Request a new source by [creating a new issue](https://github.com/mHaisham/novelsave/issues/new/choose)

| Sources | Search | Login |
| -- | :--: | :--: |
| [webnovel.com] |  | ✔ |
| [wuxiaworld.co] |  |  |
| [boxnovel.com] |  |  |
| [readlightnovel.org] |  |  |
| [insanitycave.poetry] |  |  |
| [ktlchamber.wordpress] |  |  |
| [kieshitl.wordpress] |  |  |
| [scribblehub.com] |  |  |
| [mtlnovel.com] |  |  |
| ~~[fanfiction.net]~~ |  |  |
| [novelfull.com] |  |  |
| [wuxiaworld.com] |  |  |
| [royalroad.com] |  |  |
| [wattpad.com] |  |  |
| [forums.spacebattles.com] |  |  |
| [forums.sufficientvelocity.com] |  |  |
| [dragontea.ink] |  |  |

## Metadata Sources

> Request a new source by [creating a new issue](https://github.com/mHaisham/novelsave/issues/new/choose)

| Metadata Source | Support |
| -- | :--: |
| [wlnupdates.com] | ✔ |
| [novelupdates.com] | ✔ |

<!-- SOURCE LINKS -->

[webnovel.com]: https://www.webnovel.com
[wuxiaworld.co]: https://www.wuxiaworld.co
[boxnovel.com]: https://www.boxnovel.co
[readlightnovel.org]: https://www.readlightnovel.org
[insanitycave.poetry]: https://insanitycave.poetry.blog
[ktlchamber.wordpress]: https://ktlchamber.wordpress.com
[kieshitl.wordpress]: https://kieshitl.wordpress.com
[scribblehub.com]: https://www.scribblehub.com
[mtlnovel.com]: https://www.mtlnovel.com
[fanfiction.net]: https://www.fanfiction.net
[novelfull.com]: https://novelfull.com
[wuxiaworld.com]: https://www.wuxiaworld.com
[royalroad.com]: https://www.royalroad.com
[wattpad.com]: https://www.wattpad.com
[forums.spacebattles.com]: https://forums.spacebattles.com
[forums.sufficientvelocity.com]: https://forums.sufficientvelocity.com
[dragontea.ink]: https://dragontea.ink

<!-- META SOURCE LINKS -->

[wlnupdates.com]: https://www.wlnupdates.com
[novelupdates.com]: https://www.novelupdates.com
