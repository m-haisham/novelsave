import argparse
from novelsave import NovelSave

parser = argparse.ArgumentParser(description='tool to convert webnovel to epub')
parser.add_argument('novel', help='either id or url or novel')
parser.add_argument('-u', '--update', type=bool, action='store_true', help='update webnovel details')
parser.add_argument('-p', '--pending', type=bool, action='store_true', help='download pending')
parser.add_argument('-c', '--create', type=bool, action='store_true', help='create epub')

args = parser.parse_args()

# novel id
if 'https' in args.novel:
    novel_id = int(args.novel.split('/')[4])
else:
    novel_id = int(args.novel)

novelsave = NovelSave(novel_id)

input()

if args.update:
    novelsave.update_data()

if args.pending:
    novelsave.download_pending()

if args.create:
    novelsave.create_epub()