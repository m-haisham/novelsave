import argparse
from novelsave import NovelSave

parser = argparse.ArgumentParser(description='tool to convert webnovel to epub')
parser.add_argument('novel_id', help='id of targeted webnovel')
parser.add_argument('-u', '--update', type=bool, action='store_true', help='update webnovel details')
parser.add_argument('-p', '--pending', type=bool, action='store_true', help='download pending')
parser.add_argument('-c', '--create', type=bool, action='store_true', help='create epub')

args = parser.parse_args()

novelsave = NovelSave(args.novel_id)

if args.update:
    novelsave.update_data()

if args.pending:
    novelsave.download_pending()

if args.create:
    novelsave.create_epub()