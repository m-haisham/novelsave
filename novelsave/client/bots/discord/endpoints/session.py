import nextcord
from dependency_injector.wiring import Provide
from nextcord import Interaction
from nextcord.ext import commands

from .. import utils
from ..checks import assert_check, is_direct_only
from ..session import SessionHandler


class SessionCog(commands.Cog, name="Session"):
    """This controls sessions on a per user basis"""

    session_handler: SessionHandler = Provide["session.session_handler"]

    @nextcord.slash_command(description="Show status of the session", force_global=True)
    async def status(self, intr: Interaction):
        """Show status of the session"""
        if not await assert_check(intr, is_direct_only):
            return

        try:
            await self.session_handler.get(intr).state(intr)
        except KeyError:
            await intr.send(utils.error("You have no active session."))

    @nextcord.slash_command(description="Force close the session", force_global=True)
    async def close(self, intr: Interaction):
        """Force close the session"""
        if not await assert_check(intr, is_direct_only):
            return

        try:
            await self.session_handler.get(intr).close_and_inform()
        except KeyError:
            await intr.send(utils.error("You have no active session."))
