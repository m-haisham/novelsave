from dependency_injector.wiring import Provide
from loguru import logger
from nextcord.ext import commands

from .. import checks, mfmt
from ..session import SessionHandler


class SessionCog(commands.Cog, name="Session"):
    """This controls sessions on a per user basis"""

    session_handler: SessionHandler = Provide["session.session_handler"]

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await checks.direct_only(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CheckFailure):
            await ctx.send(mfmt.error(str(error)))

        logger.exception(repr(error))

    @commands.command()
    async def status(self, ctx: commands.Context):
        """Show status of the session"""
        try:
            await self.session_handler.get(ctx).state(ctx)
        except KeyError:
            await ctx.send(mfmt.error("You have no active session."))

    @commands.command()
    async def close(self, ctx: commands.Context):
        """Force close the session"""
        try:
            self.session_handler.get(ctx).close_and_inform()
        except KeyError:
            await ctx.send(mfmt.error("You have no active session."))
