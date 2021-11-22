from datetime import datetime
from typing import Dict, Callable

from loguru import logger
from nextcord.ext import commands

from .session_helper import session_key
from .session import Session
from ..bot import bot


class SessionHandler:
    def __init__(
        self, session_factory: Callable[[commands.Bot, commands.Context], Session]
    ):
        self.sessions: Dict[str, Session] = {}
        self.session_factory = session_factory

    def get(self, ctx: commands.Context) -> Session:
        return self.sessions.get(session_key(ctx))

    def get_or_create(self, ctx: commands.Context):
        return self.sessions.setdefault(
            session_key(ctx), self.session_factory(bot, ctx)
        )

    def cleanup(self):
        current_time = datetime.now()

        expired = []
        for key, handler in self.sessions.items():
            if handler.is_closed:
                expired.append(key)
            elif handler.is_expired(current_time):
                logger.debug(f"Closing expired session: {handler.ctx.author.id}.")
                handler.close()
                expired.append(key)

        for key in expired:
            self.sessions.pop(key)
