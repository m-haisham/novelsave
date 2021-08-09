from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from novelsave.services import FileService, NovelService
from novelsave.services.source import SourceGateway, SourceGatewayProvider
from novelsave.utils.adapters import SourceAdapter, DTOAdapter


class Adapters(containers.DeclarativeContainer):
    source_adapter = providers.Factory(
        SourceAdapter,
    )

    dto_adapter = providers.Factory(
        DTOAdapter,
    )


class Infrastructure(containers.DeclarativeContainer):
    config = providers.Configuration()

    engine = providers.Singleton(create_engine, url=config.database.url, future=True)
    session_builder = providers.Singleton(sessionmaker, bind=engine, future=True)


class Services(containers.DeclarativeContainer):
    data_config = providers.Configuration()

    adapters = providers.DependenciesContainer()
    infrastructure = providers.DependenciesContainer()

    file_service = providers.Factory(
        FileService,
        location=data_config.dir,
        data_division=data_config.division_rules,
    )

    novel_service = providers.Factory(
        NovelService,
        session_builder=infrastructure.session_builder,
        dto_adapter=adapters.dto_adapter,
    )

    source_gateway_provider = providers.Factory(
        SourceGatewayProvider,
        source_adapter=adapters.source_adapter,
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration(strict=True)

    adapters = providers.Container(
        Adapters,
    )

    infrastructure = providers.Container(
        Infrastructure,
        config=config.infrastructure,
    )

    services = providers.Container(
        Services,
        data_config=config.data,
        adapters=adapters,
        infrastructure=infrastructure,
    )
