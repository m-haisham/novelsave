import argparse
from getpass import getpass
from pathlib import Path

from webnovel.tools import UrlTools

from novelsave import NovelSave
from novelsave.database import UserConfig
from novelsave.ui import ConsolePrinter


def setup_config(args):
    console = ConsolePrinter(verbose=True)
    user = UserConfig()

    # updating storage directory
    if args.dir:

        # could throw an OSError: illegal directory names
        args.dir = Path(args.dir).resolve().absolute()

        try:
            user.directory.put(str(args.dir))
            console.print(f'Updated {user.directory.name}', prefix=ConsolePrinter.P_SUCCESS)
        except ValueError as e:  # check for validation failures
            console.print(e, prefix=ConsolePrinter.P_ERROR)

        # breathe,
        print()

    # show the final results
    print('-' * 15)
    for config in user.configs:
        console.print(config.name, config.get())
    print('-' * 15)


def process_task(args):
    # soup novel url
    if 'https://' not in args.action:
        args.action = UrlTools.to_novel_url(args.action)

    if args.dir:
        args.dir = Path(args.dir).resolve()

    novelsave = NovelSave(args.action, directory=args.dir)
    novelsave.timeout = args.timeout
    novelsave.console.verbose = args.verbose
    login(args, novelsave)

    if not any([args.update, args.remove_meta, args.meta, args.pending, args.create, args.force_create]):
        novelsave.console.print('No actions selected', prefix=ConsolePrinter.P_ERROR)

    if args.update:
        novelsave.update(force_cover=args.force_cover)

    if args.remove_meta:
        novelsave.remove_metadata(with_source=True)
        novelsave.console.print('Removed metadata', prefix=ConsolePrinter.P_SUCCESS)

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
    cookie_browsers = (args.cookies_chrome, args.cookies_firefox)

    # if both login creds and cookie browser provided
    if any((args.username, args.password)) and any(cookie_browsers):
        raise ValueError("Choose one option from login and browser cookies")

    # more than one cookie browser provided
    elif len([b for b in cookie_browsers if b]) > 1:
        raise ValueError("Select single param from ('--cookies-chrome', '--cookies-firefox')")

    # apply credentials
    elif len([b for b in cookie_browsers if b]) == 1:
        browser = None
        if args.cookies_chrome:
            browser = 'chrome'
        elif args.cookies_firefix:
            browser = 'firefox'
        assert browser, "'browser' must not be None"

        novelsave.login(cookie_browser=browser)

    # login
    elif args.username:
        novelsave.username = args.username

        if not args.password:
            novelsave.password = getpass('\n[-] password: ')

        # login
        if novelsave.password:
            novelsave.login()


def main():
    parser = argparse.ArgumentParser(description='tool to convert novels to epub')
    parser.add_argument('action', type=str, help="novel url for downloading novels; 'config' to change configurations")

    actions = parser.add_argument_group(title='actions')
    actions.add_argument('-u', '--update', action='store_true', help='update novel details')
    actions.add_argument('-p', '--pending', action='store_true', help='download pending chapters')
    actions.add_argument('-c', '--create', action='store_true', help='create epub from downloaded chapters')
    actions.add_argument('--meta', type=str, help='metadata source url', default=None)
    actions.add_argument('--remove-meta', action='store_true', help='remove current metadata')
    actions.add_argument('--force-cover', action='store_true', help='download and overwrite the existing cover')
    actions.add_argument('--force-create', action='store_true', help='force create epub')
    actions.add_argument('--force-meta', action='store_true', help='force update metadata')

    auth = parser.add_argument_group(title='authentication')
    auth.add_argument('--username', type=str, help='username or email field')
    auth.add_argument('--password', type=str, help='password field')
    auth.add_argument('--cookies-chrome', action='store_true', help='use cookies from chrome')
    auth.add_argument('--cookies-firefox', action='store_true', help='use cookies from firefox')

    parser.add_argument('-v', '--verbose', help='extra information', action='store_true')
    parser.add_argument('--threads', type=int, help='number of download threads', default=4)
    parser.add_argument('--timeout', type=int, help='webdriver timeout', default=60)
    parser.add_argument('--limit', type=int, help='amount of chapters to download')

    config = parser.add_argument_group(title='config')
    config.add_argument('-d', '--dir', help='directory for saving novels')

    args = parser.parse_args()

    # Configurations
    if args.action == 'config':
        setup_config(args)
    else:
        process_task(args)


if __name__ == '__main__':
    main()
