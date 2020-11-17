import sys
import argparse
from getpass import getpass
from pathlib import Path

from webnovel.tools import UrlTools

from novelsave import NovelSave
from novelsave.database import UserConfig
from novelsave.tools import UiTools


def setup_config(args):
    user = UserConfig()

    # updating storage directory
    if args.dir:

        # could throw an OSError: illegal directory names
        args.dir = Path(args.dir).resolve().absolute()

        try:
            user.directory.put(str(args.dir))
            UiTools.print_success(f'Updated {user.directory.name}')
        except ValueError as e:  # check for validation failures
            UiTools.print_error(e)

        # breathe,
        print()

    # show the final results
    print('-' * 15)
    user.print_configs()
    print('-' * 15)


def process_task(args):
    # soup novel url
    if 'https://' not in args.action:
        args.action = UrlTools.to_novel_url(args.action)

    if args.dir:
        args.dir = Path(args.dir).resolve()

    novelsave = NovelSave(args.action, directory=args.dir)
    novelsave.timeout = args.timeout
    novelsave.verbose = args.verbose

    # get credentials
    if args.email is not None:
        novelsave.email = args.email

        print()  # some breathing room
        novelsave.password = getpass('[-] password: ')

    if not any([args.update, args.pending, args.create, args.force_create]):
        UiTools.print_error('No actions selected')

    if args.update:
        novelsave.update(force_cover=args.force_cover)

    if args.pending:
        novelsave.download(thread_count=args.threads, limit=args.limit)

    if args.create or args.force_create:
        novelsave.create_epub(force=args.force_create)


def main():
    parser = argparse.ArgumentParser(description='tool to convert novels to epub')
    parser.add_argument('action', type=str, help="novel url for downloading novels; 'config' to change configurations")

    actions = parser.add_argument_group(title='actions')
    actions.add_argument('-u', '--update', action='store_true', help='update novel details')
    actions.add_argument('-p', '--pending', action='store_true', help='download pending chapters')
    actions.add_argument('-c', '--create', action='store_true', help='create epub from downloaded chapters')
    actions.add_argument('-fc', '--force-create', action='store_true', help='force create epub')
    actions.add_argument('--force-cover', action='store_true', help='download and overwrite the existing cover')

    credentials = parser.add_argument_group(title='credentials')
    credentials.add_argument('--email', type=str, help='webnovel email')

    parser.add_argument('-v', '--verbose', help='enable animations; only in pending', action='store_true')
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
