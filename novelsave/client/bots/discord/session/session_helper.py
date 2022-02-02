from nextcord import Interaction


def session_key(intr: Interaction) -> str:
    return str(intr.user.id)
