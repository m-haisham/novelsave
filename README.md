# NovelSave

![PyPI](https://img.shields.io/pypi/v/novelsave)
![Python Version](https://img.shields.io/badge/Python-v3.8-blue)
![Repo Size](https://img.shields.io/github/repo-size/mensch272/novelsave)
[![Contributors](https://img.shields.io/github/contributors/mensch272/novelsave)](https://github.com/mensch272/novelsave/graphs/contributors)
![Last Commit](https://img.shields.io/github/last-commit/mensch272/novelsave/master)
![Issues](https://img.shields.io/github/issues/mensch272/novelsave)
![Pull Requests](https://img.shields.io/github/issues-pr/mensch272/novelsave)
[![License](https://img.shields.io/github/license/mensch272/novelsave)](LICENSE)

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

Currently only supports **epub** format. There are plans to expand support.

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

#### Novel Directory

You can change your desired novels package's saving location using the following command. Novels are by default saved to folder `novels` in user home.

```bash
novelsave config novel_dir set <dir>
```

And to reset to default, use the command shown below.

```bash
novelsave config novel_dir reset
```

For more information, run

```bash
novelsave config novel_dir --help
```

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

`chrome` `firefox` `chromium` `opera` `edge`

## Sources

Sources have been moved to its own [package](https://github.com/mensch272/novelsave_sources). You can install and upgrade sources using the following command.

```bash
pip install novelsave-sources --upgrade
```

## Disclaimer

We are not affiliated, associated, authorized, endorsed by, or in any way officially connected with the any of the [sources](#sources) mentioned above.

## License

[Apache-2.0](https://github.com/mensch272/novelsave/blob/master/LICENSE)

