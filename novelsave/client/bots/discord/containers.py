from dependency_injector import containers, providers

from .endpoints import DownloadHandler, SearchHandler
from .session import SessionHandler, Session


class SessionContainer(containers.DeclarativeContainer):
    config = providers.Configuration(strict=True)

    session_factory = providers.Selector(
        config.search.disabled,
        no=providers.Singleton(
            Session.factory,
            session_retain=config.session.retain,
            fragments=[DownloadHandler, SearchHandler],
        ),
        yes=providers.Singleton(
            Session.factory,
            session_retain=config.session.retain,
            fragments=[DownloadHandler],
        ),
    )

    session_handler = providers.Singleton(
        SessionHandler, session_factory=session_factory
    )


class DiscordApplication(containers.DeclarativeContainer):
    discord_config = providers.Configuration(strict=True)

    session = providers.Container(
        SessionContainer,
        config=discord_config,
    )
