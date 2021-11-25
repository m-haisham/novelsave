import sys

from novelsave.client import cli

if __name__ == "__main__":
    if sys.argv[1:] == ["runbot", "discord"]:
        from novelsave.client.bots import discord

        discord.main()
    else:
        cli.main()
