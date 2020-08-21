import argparse
from getpass import getpass

from webnovel.tools import UrlTools

from novelsave import NovelSave

parser = argparse.ArgumentParser(description='tool to convert novels to epub')
parser.add_argument('novel', type=str, help='either id (only for webnovels) or url of novel')
parser.add_argument('-tc', '--threads', type=int, help='number of download threads', default=4)
parser.add_argument('-to', '--timeout', type=int, help='webdriver timeout', default=60)

actions = parser.add_argument_group(title='actions')
actions.add_argument('-u', '--update', action='store_true', help='update novel details')
actions.add_argument('-p', '--pending', action='store_true', help='download pending chapters')
actions.add_argument('-c', '--create', action='store_true', help='create epub from downloaded chapters')

credentials = parser.add_argument_group(title='credentials')
credentials.add_argument('--email', type=str,  help='webnovel email')

args = parser.parse_args()

# soup novel url
if 'https://' not in args.novel:
    args.novel = UrlTools.to_novel_url(args.novel)

novelsave = NovelSave(args.novel)
novelsave.timeout = args.timeout

# get credentials
if args.email is not None:
    novelsave.email = args.email

    print()  # some breathing room
    novelsave.password = getpass('[-] password')

if not any([args.update, args.pending, args.create]):
    print('[✗] No actions selected')

if args.update:
    novelsave.update()

if args.pending:
    novelsave.download(thread_count=args.threads)

if args.create:
    novelsave.create_epub()