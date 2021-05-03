import sys

from novelsave import NovelSave
from novelsave.cli import CliListing, CliConfig, DefaultSubcommandArgumentParser
from novelsave.database import UserConfig
from novelsave.exceptions import MissingSource, ResponseException, NoInputException, CookieAuthException
from novelsave.utils.helpers import url_pattern
from novelsave.utils.ui import ConsoleHandler, figlet


def process_task(args):
    console = ConsoleHandler(plain=args.plain)

    # checks if the provided url is valid
    if not url_pattern.match(args.url):
        console.error('Provided url is not valid. Please check and try again')
        sys.exit(1)

    try:
        novelsave = NovelSave(args.url, args.no_input, plain=args.plain)
    except MissingSource as e:
        console.error(str(e))
        sys.exit(1)

    novelsave.timeout = args.timeout

    try:
        login(args, novelsave)
    except Exception as e:
        console.error(str(e))
        sys.exit(1)

    if not any([args.update, args.remove_meta, args.meta, args.pending, args.create, args.force_create]):
        console.error('No actions selected')
        console.newline()

    if args.update:
        try:
            novelsave.update(force_cover=args.force_cover)
        except ResponseException as e:
            console.error(e.message)
            sys.exit(1)

    if args.remove_meta:
        novelsave.remove_metadata(with_source=True)

    if args.meta:
        novelsave.metadata(url=args.meta, force=args.force_meta)

    if args.pending:
        try:
            novelsave.download(thread_count=args.threads, limit=args.limit)
        except ValueError as e:
            console.error(str(e))
            sys.exit(1)

    if args.create or args.force_create:
        novelsave.create_epub(force=args.force_create)


def login(args, novelsave):
    """
    cookie_auth and browser cookie
    """
    # apply credentials
    if args.cookies_from:
        args.cookies_from = args.cookies_from.lower()
        novelsave.cookie_auth(cookie_browser=args.cookies_from)

    # cookie_auth
    elif args.username:
        novelsave.username = args.username

        def resolve_and_auth():
            if args.password:
                novelsave.password = args.password
            else:
                try:
                    novelsave.password = novelsave.console.getpass(f'Enter your password: ({args.username}) ')
                except NoInputException:
                    raise Exception(NoInputException.messages['cred_password'])

            novelsave.credential_auth()

        if args.force_login:
            resolve_and_auth()
        else:
            try:
                novelsave.cookie_auth()
            except CookieAuthException:
                resolve_and_auth()


def main():
    parser = DefaultSubcommandArgumentParser(
        prog='novelsave',
        description='This is a tool to download and convert webnovels from popular sites to epub',
    )

    parser.add_argument('--plain', help='restrict display output in plain, tabular text format', action='store_true')
    parser.add_argument('--no-input', help='don’t prompt or do anything interactive', action='store_true')

    sub = parser.add_subparsers()

    novel = sub.add_parser('novel', help='download, update, and delete novels')
    novel.add_argument('url', type=str, help="url of the specific novel")

    # exposed actions
    actions = novel.add_argument_group(title='actions')
    actions.add_argument('-u', '--update', action='store_true', help='update novel details')
    actions.add_argument('-p', '--pending', action='store_true', help='download pending chapters')
    actions.add_argument('-c', '--create', action='store_true', help='create epub from downloaded chapters')
    actions.add_argument('--meta', type=str, help='metadata source url', default=None)
    actions.add_argument('--remove-meta', action='store_true', help='remove current metadata')
    actions.add_argument('--force-cover', action='store_true', help='download and overwrite the existing cover')
    actions.add_argument('--force-create', action='store_true', help='force create epub ignoring update status')
    actions.add_argument('--force-meta', action='store_true', help='force update metadata ignoring previous metadata')

    # auth
    auth = novel.add_argument_group(title='auth')
    auth_cookies = auth.add_mutually_exclusive_group()
    auth_cookies.add_argument('--username', type=str, help='username or email field')
    auth.add_argument('--password', type=str, help='password field; not recommended, refer to README for more details')
    auth.add_argument('--force-login', action='store_true', help='remove existing cookies and login')
    auth_cookies.add_argument('--cookies-from', help='use cookies from specified browser')

    # misc
    novel.add_argument('--threads', type=int, help='number of download threads', default=4)
    novel.add_argument('--timeout', type=int, help='webdriver timeout', default=60)
    novel.add_argument('--limit', type=int, help='amount of chapters to download')
    novel.set_defaults(func=process_task)

    # Novel listing
    listing = sub.add_parser('list', help='manipulate currently existing novels')
    listing.add_argument('--novel', type=str,
                         help='takes the url of the novel and displays meta information')
    deleting = listing.add_mutually_exclusive_group()
    deleting.add_argument('--reset', action='store_true',
                          help='remove chapters and metadata. to be used with --novel')
    deleting.add_argument('--delete', action='store_true',
                          help='remove everything including compiled epub files. to be used with --novel')
    listing.add_argument('--yes', action='store_true', help='skip confirm confirmation used in --reset and --delete')
    listing.set_defaults(func=CliListing.handle)

    # Configurations
    config = sub.add_parser('config', help='update and view user configurations')
    config.add_argument('--save-dir', help='directory for saving novels')
    config.add_argument('--toggle-banner', action='store_true', help='Toggle show and hide for title banner')
    config.set_defaults(func=CliConfig.handle)

    parser.set_default_subparser('novel')

    args = parser.parse_args()

    if not args.plain and UserConfig.instance().show_banner.get():
        print(figlet.banner)

    try:
        args.func(args)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
