# NovelSave

![PyPI](https://img.shields.io/pypi/v/novelsave)
![Python Version](https://img.shields.io/badge/Python-v3.8-blue)
![Repo Size](https://img.shields.io/github/repo-size/mHaisham/novelsave)
[![Contributors](https://img.shields.io/github/contributors/mHaisham/novelsave)](https://github.com/mHaisham/novelsave/graphs/contributors)
![Last Commit](https://img.shields.io/github/last-commit/mHaisham/novelsave/master)
![Issues](https://img.shields.io/github/issues/mHaisham/novelsave)
![Pull Requests](https://img.shields.io/github/issues-pr/mHaisham/novelsave)
[![License](https://img.shields.io/github/license/mHaisham/novelsave)](LICENSE)

This is a tool to download and convert webnovels from popular sites to epub.

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

### Basic

The most common arguments you'll be using are

- `-u` `--update`  - downloads novel webpage and updates novel information on disk. This includes title, author and chapters (including pending chapters).
- `-p` `--pending` - download all the pending chapters. Typically uses 4 threads to download chapter pages unless otherwise specified (`--thread-count <count>`).
- `-c` `--create` - packs the (downloaded chapters of) novel into an epub file.

```bash
novelsave <url> -u -p -c
```

By combining these 3 flags you can update, download, and create epub in a single line.

### Pipe

If you are calling novelsave via another program or want to pipe the output to another program like `grep`, add the `--plain` flag.

This ensures that the output would be as concise as possible.

```bash
novelsave --plain <url> -u -p -c
```

### Configurations

You can check the programs configurations as shown below

```bash
novelsave config
```

#### Banner

``````
                              ___                                       
                             /\_ \                                      
  ___     ___   __  __     __\//\ \     ____     __     __  __     __   
/' _ `\  / __`\/\ \/\ \  /'__`\\ \ \   /',__\  /'__`\  /\ \/\ \  /'__`\ 
/\ \/\ \/\ \L\ \ \ \_/ |/\  __/ \_\ \_/\__, `\/\ \L\.\_\ \ \_/ |/\  __/ 
\ \_\ \_\ \____/\ \___/ \ \____\/\____\/\____/\ \__/.\_\\ \___/ \ \____\
 \/_/\/_/\/___/  \/__/   \/____/\/____/\/___/  \/__/\/_/ \/__/   \/____/
  v(version) - https://github.com/mHaisham/novelsave
``````

Banner is by default displayed at start-up of the program unless its run in plain mode.

You can change the display settings of banner as shown below.

```bash
novelsave config --toggle-banner
```

#### Save directory

Novels are by default saved to folder `novels` in user home.

Change the novels download directory as shown below.

```bash
novelsave config --save-dir <dir>
```

## Help

### `novelsave --help`

```bash
usage: novelsave [-h] [--plain] [--no-input] {novel,list,config} ...

This is a tool to download and convert webnovels from popular sites to epub

positional arguments:
  {novel,list,config}
    novel              download, update, and delete novels
    list               manipulate currently existing novels
    config             update and view user configurations

optional arguments:
  -h, --help           show this help message and exit
  --plain              restrict display output in plain, tabular text format
  --no-input           don’t prompt or do anything interactive
```

### `novelsave novel --help`	

```bash
usage: novelsave novel [-h] [-u] [-p] [-c] [--meta META] [--remove-meta] [--force-cover] [--force-create] [--force-meta] [--username USERNAME]
                       [--password PASSWORD] [--force-login] [--cookies-from COOKIES_FROM] [--threads THREADS] [--timeout TIMEOUT] [--limit LIMIT]
                       url

positional arguments:
  url                   url of the specific novel

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
  --force-create        force create epub ignoring update status
  --force-meta          force update metadata ignoring previous metadata

auth:
  --username USERNAME   username or email field
  --password PASSWORD   password field; not recommended, refer to README for more details
  --force-login         remove existing cookies and login
  --cookies-from COOKIES_FROM
                        use cookies from specified browser
```

### `novelsave list --help`

```
usage: novelsave list [-h] [--novel NOVEL] [--reset | --delete] [--yes]

optional arguments:
  -h, --help     show this help message and exit
  --novel NOVEL  takes the url of the novel and displays meta information
  --reset        remove chapters and metadata. to be used with --novel
  --delete       remove everything including compiled epub files. to be used with --novel
  --yes          skip confirm confirmation used in --reset and --delete
```

### `novelsave config --help`

```bash
usage: novelsave config [-h] [--save-dir SAVE_DIR] [--toggle-banner]

optional arguments:
  -h, --help           show this help message and exit
  --save-dir SAVE_DIR  directory for saving novels
  --toggle-banner      Toggle show and hide for title banner
```

## Login and cookies

Two methods of accessing authenticated content are provided

### Browser cookies (Recommended)

Uses cookies from available browsers access content

use syntax `--use-cookies [browser]`. for example

```bash
novelsave <url> -u -p -c --cookies-from firefox
```

Requires to be Signed in, in the browser of choice

**Available**

`chrome` `firefox` `chromium` `opera` `edge`

### Login

Username and password are sent to the website server to authenticate.

Cookies are persisted and stored at config's location.

Novelsave attempts to use the available cookies unless:

- any of the cookies from relevant domains are expired

- user provides the flag `--force-login`

refer to [sources](#sources) to check supported sites.

## Module

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
- ```cookie_auth(self, cookie_browser: Union[str, None] = None)```
- ```credential_auth(self)```

### Database

you can access the database by using the `db` attribute of `NovelSave`

```python
    save.db
```

## Sources

> Request a new source by [creating a new issue](https://github.com/mHaisham/novelsave/issues/new/choose)

### Novel

| Sources | Login |                 Reason                  |
| -- | :--: | :--: |
| [webnovel.com] | ✔ |  |
| [wuxiaworld.co] |  |  |
| [boxnovel.com] |  |  |
| [readlightnovel.org] |  |  |
| [insanitycave.poetry] |  |  |
| [ktlchamber.wordpress] |  |  |
| [kieshitl.wordpress] |  |  |
| [scribblehub.com] |  |  |
| [mtlnovel.com] |  |  |
| ~~[fanfiction.net]~~ |  | Broken due to cloudflare bot protection |
| [novelfull.com] |  |  |
| [wuxiaworld.com] |  |  |
| [royalroad.com] |  |  |
| [wattpad.com] |  |  |
| [forums.spacebattles.com] |  |  |
| [forums.sufficientvelocity.com] |  |  |
| [dragontea.ink] |  |  |
| [novelsite.net] |  |  |
| [foxaholic.com] |  |  |
| [chrysanthemumgarden.com] |  |  |
| [peachpitting.com] |  |  |
| [betwixtedbutterfly.com] |  |  |
| [dummynovels.com] |  |  |
| [chickengege.org] |  |  |
| [wuxiaworld.online] |  |  |
| [novelonlinefull.com] |  |  |
| [novelpassion.com] |  |  |
| [novelfun.net] |  |  |
| [novelhall.com] |  |  |
| [novelsrock.com] |  |  |
| [creativenovels.com] |  |  |
| [wuxiaworld.site] |  |  |
| [novelgate.net] |  |  |

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
[novelsite.net]: https://novelsite.net
[foxaholic.com]: https://foxaholic.com
[chrysanthemumgarden.com]: https://chrysanthemumgarden.com
[peachpitting.com]: https://peachpitting.com
[betwixtedbutterfly.com]: https://betwixtedbutterfly.com
[dummynovels.com]: https://dummynovels.com
[chickengege.org]: https://www.chickengege.org
[wuxiaworld.online]: https://wuxiaworld.online
[novelonlinefull.com]: https://novelonlinefull.com
[novelpassion.com]: https://www.novelpassion.com
[novelfun.net]: https://novelfun.net
[novelhall.com]: https://www.novelhall.com
[novelsrock.com]: https://novelsrock.com
[creativenovels.com]: https://creativenovels.com
[wuxiaworld.site]: https://wuxiaworld.site
[novelgate.net]: https://novelgate.net

### Metadata

| Metadata Source | Support |
| -- | :--: |
| [wlnupdates.com] | ✔ |
| [novelupdates.com] | ✔ |

<!-- META SOURCE LINKS -->

[wlnupdates.com]: https://www.wlnupdates.com
[novelupdates.com]: https://www.novelupdates.com

## Disclaimer

We are not affiliated, associated, authorized, endorsed by, or in any way officially connected with the any of the [sources](#sources) mentioned above.

## License

[Apache-2.0](https://github.com/mHaisham/novelsave/blob/master/LICENSE)

