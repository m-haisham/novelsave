import argparse
from getpass import getpass
from pathlib import Path

from webnovel.tools import UrlTools

from novelsave import NovelSave
from novelsave.database import UserConfig
from novelsave.ui import ConsolePrinter, PrinterPrefix, TableBuilder
from novelsave.commandline import NovelListing


def setup_config(args):
    console = ConsolePrinter(verbose=True)
    user = UserConfig()

    # updating storage directory
    if args.dir:

        # could throw an OSError: illegal directory names
        args.dir = Path(args.dir).resolve().absolute()

        try:
            user.directory.put(str(args.dir))
            console.print(f'Updated {user.directory.name}', prefix=PrinterPrefix.SUCCESS)
        except ValueError as e:  # check for validation failures
            console.print(e, prefix=PrinterPrefix.ERROR)

        # breathe,
        print()

    table = TableBuilder(('field', 'value'))
    for config in user.configs:
        table.add_row((config.name, config.get()))

    print(table)


def process_task(args):
    # checks if the provided url is valid
    if 'https://' not in args.url:
        # non valid urls are converted to webnovel urls
        # or atleast tried to
        args.url = UrlTools.to_novel_url(args.url)

    novelsave = NovelSave(args.url, verbose=args.verbose)
    novelsave.timeout = args.timeout
    login(args, novelsave)

    if not any([args.update, args.remove_meta, args.meta, args.pending, args.create, args.force_create]):
        novelsave.console.print('No actions selected', prefix=PrinterPrefix.ERROR)

    if args.update:
        novelsave.update(force_cover=args.force_cover)

    if args.remove_meta:
        novelsave.remove_metadata(with_source=True)
        novelsave.console.print('Removed metadata', prefix=PrinterPrefix.SUCCESS)

    if args.meta:
        novelsave.metadata(url=args.meta, force=args.force_meta)

    if args.pending:
        novelsave.download(thread_count=args.threads, limit=args.limit)

    if args.create or args.force_create:
        novelsave.create_epub(force=args.force_create)


def login(args, novelsave):
    """
    login and browser cookie
    """
    browser_names = ('chrome', 'firefox', 'chromium', 'opera', 'edge')

    # apply credentials
    if args.use_cookies:
        args.use_cookies = args.use_cookies.lower()
        if args.use_cookies not in browser_names:
            raise ValueError(f"extracting cookies from '{args.use_cookies}' is not supported")

        novelsave.login(cookie_browser=args.use_cookies, force=args.force_login)

    # login
    elif args.username:
        novelsave.username = args.username

        if not args.password:
            novelsave.password = getpass('\n[-] password: ')

        # login
        if novelsave.password:
            novelsave.login()


def main():
    parser = argparse.ArgumentParser(prog='novelsave', description='tool to convert novels to epub')
    parser.add_argument('-v', '--verbose', help='extra information', action='store_true')

    sub = parser.add_subparsers()

    novel = sub.add_parser('novel', help='download, update, and delete novels')
    novel.add_argument('url', type=str, help="novel url or identifier for downloading novels")

    # exposed actions
    actions = novel.add_argument_group(title='actions')
    actions.add_argument('-u', '--update', action='store_true', help='update novel details')
    actions.add_argument('-p', '--pending', action='store_true', help='download pending chapters')
    actions.add_argument('-c', '--create', action='store_true', help='create epub from downloaded chapters')
    actions.add_argument('--meta', type=str, help='metadata source url', default=None)
    actions.add_argument('--remove-meta', action='store_true', help='remove current metadata')
    actions.add_argument('--force-cover', action='store_true', help='download and overwrite the existing cover')
    actions.add_argument('--force-create', action='store_true', help='force create epub')
    actions.add_argument('--force-meta', action='store_true', help='force update metadata')

    # auth
    auth = novel.add_argument_group(title='auth')
    auth_cookies = auth.add_mutually_exclusive_group()
    auth_cookies.add_argument('--username', type=str, help='username or email field')
    auth.add_argument('--password', type=str, help='password field; not recommended, refer to README for more details')
    auth.add_argument('--force-login', action='store_true', help='remove existing cookies and login')
    auth_cookies.add_argument('--use-cookies', help='use cookies from specified browser')

    # misc
    novel.add_argument('--threads', type=int, help='number of download threads', default=4)
    novel.add_argument('--timeout', type=int, help='webdriver timeout', default=60)
    novel.add_argument('--limit', type=int, help='amount of chapters to download')
    novel.set_defaults(func=process_task)

    # Novel listing
    listing = sub.add_parser('list', help='manipulate currently existing novels')
    listing.add_argument('--novel', type=str,
                         help='takes the url of the novel and displays meta information')
    listing.add_argument('--reset', action='store_true',
                         help='remove chapters and metadata. to be used with --novel')
    listing.add_argument('--full', action='store_true',
                         help='remove everything including compiled epub files. to be used with --reset')
    listing.set_defaults(func=parse_listing)

    # Configurations
    config = sub.add_parser('config', help='update and view user configurations')
    config.add_argument('-d', '--dir', help='directory for saving novels')
    config.set_defaults(func=setup_config)

    args = parser.parse_args()
    args.func(args)


def parse_listing(args):
    listing = NovelListing(args.verbose)

    if args.novel:
        if args.reset:
            listing.reset_novel(args.novel, args.full)
        else:
            listing.show_novel(args.novel)
    else:
        listing.show_all()


if __name__ == '__main__':
    main()
