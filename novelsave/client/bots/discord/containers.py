from dependency_injector import containers, providers

from novelsave.containers import Application
from novelsave.services.cloud.filehost import AnonFilesHost, GoFilesHost, NoneFilesHost
from .endpoints import DownloadHandler, SearchHandler
from .session import SessionHandler, Session


class CloudContainer(containers.DeclarativeContainer):
    config = providers.Configuration(strict=True)

    filehost = providers.Selector(
        config.cloud.filehost,
        anonfiles=providers.Factory(AnonFilesHost),
        gofiles=providers.Factory(GoFilesHost),
        none=providers.Factory(NoneFilesHost),
    )


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
    config = providers.Configuration(strict=True)

    application = providers.Container(
        Application,
        config=config.app,
    )

    session = providers.Container(
        SessionContainer,
        config=config.discord,
    )

    cloud = providers.Container(
        CloudContainer,
        config=config.discord,
    )
