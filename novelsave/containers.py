from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from novelsave.services import FileService, SourceService
from novelsave.utils.adapters import SourceAdapter


class AdapterContainer(containers.DeclarativeContainer):

    source_novel_adapter = providers.Factory(
        SourceAdapter,
    )


class InfrastructureContainer(containers.DeclarativeContainer):
    database_url = providers.Dependency()

    engine = providers.Singleton(create_engine, url=database_url, future=True)
    session = providers.Singleton(sessionmaker, bind=engine, future=True)


class ServiceContainer(containers.DeclarativeContainer):
    data_dir = providers.Dependency()
    data_division = providers.Dependency()

    novel_url = providers.Dependency()

    file_service = providers.Factory(
        FileService,
        location=data_dir(),
        data_division=data_division(),
    )

    source_service = providers.Singleton(
        SourceService,
        novel_url=novel_url(),
    )


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration(strict=True)

    adapter = AdapterContainer()

    infrastructure = InfrastructureContainer(
        database_url=config.database_url(),
    )

    service = ServiceContainer(
        data_dir=config.data_dir(),
        data_division=config.data_division(),
        novel_url=config.novel_url(),
    )
