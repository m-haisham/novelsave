# NovelSave

![PyPI](https://img.shields.io/pypi/v/novelsave)
![Python Version](https://img.shields.io/badge/Python-v3.8-blue)
![Last Commit](https://img.shields.io/github/last-commit/mensch272/novelsave/main)
![Issues](https://img.shields.io/github/issues/mensch272/novelsave)
![Pull Requests](https://img.shields.io/github/issues-pr/mensch272/novelsave)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/mensch272/novelsave/main.svg)](https://results.pre-commit.ci/latest/github/mensch272/novelsave/main)
[![License](https://img.shields.io/github/license/mensch272/novelsave)](LICENSE)
![Discord](https://img.shields.io/discord/911120379341307904)

This is a tool to download and convert novels from popular sites to e-books.

> **v0.7.+ is not compatible with previous versions**

## Install

```bash
pip install novelsave
```

or

```bash
pip install git+https://github.com/mensch272/novelsave.git
```

### Chatbots

#### Discord

Join our server: https://discord.gg/eFgtrKTFt3

##### Environmental Variables

The default environmental variables are shown below. Modify them to your liking when deploying.

`DISCORD_TOKEN` is required, others are optional.

```shell
DISCORD_TOKEN=  # Required: discord bot token
DISCORD_SESSION_TIMEOUT=10 # Minutes
DISCORD_DOWNLOAD_THREADS=4
DISCORD_SEARCH_LIMIT=20  # Maximum results to show
DISCORD_SEARCH_DISABLED=no  # Disable search functionality
```

#### Heroku Deployment

Fill out the following form and set the environmental variables.

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## Usage

### Basic

To download and package the novel in a single line use the following command:

```bash
novelsave process <id_or_url>
```

The most common commands you'll be using are:

#### `update`

The command requires the url of the id of the novel as an argument. When the novel has been identified it attempts to update the current novel information in the following steps:

1. Download the novel webpage.
2. Update the novel information. This includes title, author and pending chapters.
3. Identify the chapters with no content and download and update them.
4. Download any assets that require to be downloaded (assets are identified during chapter download).

Note that, if url is provided and the novel does not already exist in the database, a new novel entry will be created.

For more information, run

```bash
novelsave update --help
```

#### `package`

The command requires the url of the id of the novel as an argument. When novel is identified compiles the downloaded content into the specified formats.

Specify a compilation target using the `--target` option. If option is not provided
compiles to only epub.

Or you may use `--target-all` to package to all supported formats.

```bash
novelsave package <id_or_url> --target epub --target web
```

Supported compilation targets:

`epub` `html` `mobi` `pdf` `azw3` `text`

For more information, run

```bash
novelsave package --help
```

#### `process`

The command requires the url of the id of the novel as an argument. This is a combination of the above two commands, `update` and `package`.

This is a command of convenience, to update and package in a single command.

For more information, run

```bash
novelsave process --help
```

### Configurations

Use the following command to show all the current configurations. Default value will be shown
in case none is set.

```bash
novelsave config show
```

You may change your configurations using `set` or `reset`. For example:

```bash
novelsave config set novel.dir --value ~/mynovels
```

```bash
novelsave config reset novel.dir
```

All supported configurations are:

- `novel.dir` - Your desired novel's packaged data (epub, mobi) save location

### More

To find more information, use option `--help` on groups and commands.

```bash
novelsave --help
```

```bash
novelsave novel --help
```

## Cookies

Want to access authentication protected content, use browser cookies.

### Browser cookies

This is an optional feature where you may use cookies from your browsers when sending requests.
This effectively allows the script to pretend as the browser and thus allowing access to any content
the browser would also be able to access.

You can use this in the following simple steps:

1. Login to your source of choice with your browser of choice (though make sure the browser is supported).
2. Use option `--browser <browser>` when updating novel (also available in process).

```bash
novelsave [update|process] <id_or_url> --browser <browser>
```

**Supported**

`chrome` `firefox` `chromium` `opera` `edge` `brave`

## Sources

Sources have been moved to its own [package](https://github.com/mensch272/novelsave_sources). You can install and upgrade sources using the following command.

```bash
pip install novelsave-sources --upgrade
```

## Disclaimer

We are not affiliated, associated, authorized, endorsed by, or in any way officially connected with the any of the [sources](#sources) mentioned above.

## License

[Apache-2.0](https://github.com/mensch272/novelsave/blob/master/LICENSE)
