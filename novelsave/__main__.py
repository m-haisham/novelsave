import argparse
from getpass import getpass

from webnovel.tools import UrlTools

from novelsave import WebNovelSave

parser = argparse.ArgumentParser(description='tool to convert webnovel to epub', epilog='Own your novels')
parser.add_argument('novel', type=str, help='either id or url of novel')
parser.add_argument('-t', '--timeout', type=int, help='webdriver timeout', default=60)

actions = parser.add_argument_group(title='actions')
actions.add_argument('-u', '--update', action='store_true', help='update webnovel details')
actions.add_argument('-p', '--pending', action='store_true', help='download pending')
actions.add_argument('-c', '--create', action='store_true', help='create epub')

credentials = parser.add_argument_group(title='credentials')
credentials.add_argument('--email', type=str,  help='webnovel email')

args = parser.parse_args()

# soup novel id
if 'https://' in args.novel:
    novel_id = UrlTools.from_novel_url(args.novel)
else:
    novel_id = int(args.novel)

novelsave = WebNovelSave(novel_id)
novelsave.timeout = args.timeout

# get credentials
if args.email is not None:
    novelsave.email = args.email
    novelsave.password = getpass('[-] password')

if not any([args.update, args.pending, args.create]):
    print('[✗] No actions selected')

if args.update:
    novelsave.update_data()

if args.pending:
    novelsave.download_pending()

if args.create:
    novelsave.create_epub()