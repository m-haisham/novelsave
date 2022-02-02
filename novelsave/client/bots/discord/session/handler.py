from datetime import datetime
from typing import Dict, Callable

from loguru import logger
from nextcord import Interaction
from nextcord.ext import commands

from .session import Session
from .session_helper import session_key
from ..bot import bot


class SessionHandler:
    def __init__(self, session_factory: Callable[[commands.Bot, Interaction], Session]):
        self.sessions: Dict[str, Session] = {}
        self.session_factory = session_factory

    def get(self, intr: Interaction) -> Session:
        """Return existing user session

        :raises KeyError: if user does not have a session
        """
        self.cleanup()
        session = self.sessions[session_key(intr)]
        return session

    def get_or_create(self, intr: Interaction):
        """Create or return already existing session"""
        try:
            return self.get(intr)
        except KeyError:
            session = self.session_factory(bot, intr)
            self.sessions[session_key(intr)] = session
            return session

    def cleanup(self):
        """Find and remove all expired sessions"""
        current_time = datetime.now()

        expired = []
        for key, handler in self.sessions.items():
            if handler.is_closed:
                expired.append(key)
            elif handler.is_expired(current_time):
                logger.debug(f"Closing expired session: {handler.intr.user.id}.")
                handler.close()
                expired.append(key)

        for key in expired:
            self.sessions.pop(key)
