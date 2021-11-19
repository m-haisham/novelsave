import sys

from novelsave.client import cli
from novelsave.client.bots import discord


if __name__ == "__main__":
    if sys.argv[1:] == ["runbot", "discord"]:
        discord.main()
    else:
        cli.main()
