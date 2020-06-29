import argparse
from novelsave import NovelSave

parser = argparse.ArgumentParser(description='tool to convert webnovel to epub')
parser.add_argument('novel', type=str, help='either id or url of novel')
parser.add_argument('--email', type=str,  help='email credential')
parser.add_argument('--pass', type=str, help='password credential', dest='password')
parser.add_argument('-u', '--update', action='store_true', help='update webnovel details')
parser.add_argument('-p', '--pending', action='store_true', help='download pending')
parser.add_argument('-c', '--create', action='store_true', help='create epub')

args = parser.parse_args()

# parse novel id
if 'https' in args.novel:
    novel_id = int(args.novel.split('/')[4])
else:
    novel_id = int(args.novel)

novelsave = NovelSave(novel_id)
novelsave.email = args.email
novelsave.password = args.password

if args.update:
    novelsave.update_data()

if args.pending:
    novelsave.download_pending()

if args.create:
    novelsave.create_epub()