import asyncio
import inspect
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import List, Type, Callable, Coroutine

from loguru import logger
from nextcord.ext import commands

from .fragment import SessionFragment
from .session_helper import session_key
from .. import mixins, mfmt
from ..exceptions import AlreadyClosedException

SessionState = Callable[[commands.Context], Coroutine]


class Session(mixins.ContainerMixin):
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

        self.executor = ThreadPoolExecutor(max_workers=10)

        self.fragments = {fragment.__name__: fragment(self) for fragment in fragments}

        self.setup_container(session_key(self.ctx))

    def renew(self, ctx: commands.Context):
        self.ctx = ctx
        return self

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

    def send_sync(self, *args, **kwargs):
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
        if self.is_busy():
            await ctx.send("Please wait…")
            await self.state(ctx)
            return

        method = self._get_fragment_property(func)
        if callable(method):
            self.last_activity = datetime.now()

        self.executor.submit(method, *args, **kwargs)

    async def call(self, func: Callable, *args, **kwargs):
        method = self._get_fragment_property(func)

        if callable(method):
            self.last_activity = datetime.now()

        if inspect.isawaitable(method):
            return await method(*args, **kwargs)
        else:
            return method(*args, **kwargs)

    def _get_fragment_property(self, func: Callable):
        _type, func = func.__qualname__.split(".", maxsplit=1)

        fragment = self.fragments[_type]
        method = getattr(fragment, func)

        return method

    def is_busy(self):
        return any(fragment.is_busy() for fragment in self.fragments.values())

    def is_expired(self, current: datetime) -> bool:
        if self.is_busy():
            return False
        elif current - self.last_activity < self.session_retain:
            return False
        else:
            return True

    async def close_and_inform(self):
        await self.ctx.send("Cleaning up temporary files…")
        try:
            self.close()
        except AlreadyClosedException as e:
            await self.ctx.send(mfmt.error(str(e)))

        await self.ctx.send("Session closed.")

    def close(self):
        if self.is_closed:
            raise AlreadyClosedException("This session is already closed.")

        for fragment in self.fragments.values():
            fragment.close()

        self.executor.shutdown(wait=False, cancel_futures=True)
        self.close_session()
        shutil.rmtree(self.path_service.config_path, ignore_errors=True)

        self.is_closed = True
