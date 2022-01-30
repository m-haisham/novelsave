import asyncio
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import List, Type, Callable, Coroutine

from dependency_injector.wiring import Provide
from loguru import logger
from nextcord.ext import commands

from .fragment import SessionFragment
from .session_helper import session_key
from .. import mixins, mfmt
from ..exceptions import AlreadyClosedException

SessionState = Callable[[commands.Context], Coroutine]


class Session(mixins.ContainerMixin):
    thread_count: int = Provide["config.discord.session.threads"]

    def __init__(
        self,
        bot: commands.Bot,
        ctx: commands.Context,
        session_retain: timedelta,
        fragments: List[Type[SessionFragment]],
    ):
        self.bot = bot
        self.ctx = ctx

        self.state: SessionState = self.initial
        self.is_closed = False

        self.last_activity = datetime.now()
        self.session_retain = session_retain

        self.executor = ThreadPoolExecutor(max_workers=self.thread_count)

        self.fragments = {fragment.__name__: fragment(self) for fragment in fragments}

        self.setup_container(session_key(self.ctx))

    def renew_context(self, ctx: commands.Context):
        self.ctx = ctx
        return self

    def has_fragment(self, type_: type):
        return type_.__name__ in self.fragments

    @classmethod
    def factory(
        cls,
        session_retain: timedelta,
        fragments: List[Type[SessionFragment]],
    ):
        def wrapped(*args, **kwargs):
            return cls(
                *args,
                **kwargs,
                session_retain=session_retain,
                fragments=fragments,
            )

        return wrapped

    @staticmethod
    async def initial(ctx):
        await ctx.send("Just spinning things up.")

    def sync(self, func, *args, **kwargs):
        """Synchronously schedule an asynchronous function"""
        asyncio.run_coroutine_threadsafe(
            func(*args, **kwargs),
            self.bot.loop,
        ).result(timeout=3 * 60)

    def send_sync(self, *args, **kwargs):
        """Synchronously send a function"""
        message = ", ".join(
            [" ".join(args), " ".join(f"{k}={v}" for k, v in kwargs.items())]
        )
        if self.is_closed:
            logger.debug("Attempted to send message when session is closed:", message)
            return

        logger.debug(message)
        asyncio.run_coroutine_threadsafe(
            self.ctx.send(*args, **kwargs),
            self.bot.loop,
        ).result(timeout=3 * 60)

    async def run(self, ctx: commands.Context, func: Callable, *args, **kwargs):
        """Schedule a fragment method to be run in the thread pool"""
        if self.is_busy():
            await ctx.send("Please wait…")
            await self.state(ctx)
            return

        self.executor.submit(self.get(func), *args, **kwargs)

    def get(self, func: Callable):
        """Call a method and return the result

        Supports sync and async functions
        """
        method = self._get_fragment_property(func)

        if callable(method):
            self.last_activity = datetime.now()

        return method

    def _get_fragment_property(self, func: Callable):
        _type, func = func.__qualname__.split(".", maxsplit=1)

        fragment = self.fragments[_type]
        method = getattr(fragment, func)

        return method

    def is_busy(self):
        """Whether the session is doing work"""
        return any(fragment.is_busy() for fragment in self.fragments.values())

    def is_expired(self, current_time: datetime) -> bool:
        """Whether the current session is expired"""
        if self.is_busy():
            return False
        elif current_time - self.last_activity < self.session_retain:
            return False
        else:
            return True

    async def close_and_inform(self):
        """Close the session and inform the user"""
        await self.ctx.send("Cleaning up temporary files…")
        try:
            self.close()
        except AlreadyClosedException as e:
            await self.ctx.send(mfmt.error(str(e)))

        await self.ctx.send("Session closed.")

    def close(self):
        """Close the current user session and remove all temporary files"""
        if self.is_closed:
            raise AlreadyClosedException("This session is already closed.")

        logger.debug(f"Closing session: {session_key(self.ctx)}")
        for fragment in self.fragments.values():
            fragment.close()

        self.executor.shutdown(wait=False, cancel_futures=True)
        self.close_engine()
        shutil.rmtree(self.path_service().config_path, ignore_errors=True)

        logger.debug("Session closed.")
        self.is_closed = True
