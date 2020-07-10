# NovelSave `Own your novels`

Tool to convert webnovel to epub

## Install

```
pip install novelsave
```

## Commandline

### Example
```
python3 -m novelsave 11022733006234505 -u -p -c
```

### Help

```batch
usage: __main__.py [-h] [-t TIMEOUT] [-u] [-p] [-c] [--email EMAIL] [--pass PASSWORD] novel

tool to convert webnovel to epub

positional arguments:
  novel                 either id or url of novel

optional arguments:
  -h, --help            show this help message and exit
  -t TIMEOUT, --timeout TIMEOUT
                        webdriver timeout

actions:
  -u, --update          update webnovel details
  -p, --pending         download pending
  -c, --create          create epub

credentials:
  --email EMAIL         webnovel email
  --pass PASSWORD       webnovel password

Own your novels
```

## Manual

Access all the saved data using `novelsave.database.NovelData`

Manipulate the data using the accessors provided in the class

Creating an epub is easy as calling a function. `novelsave.Epub().create()`
