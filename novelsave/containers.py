from dependency_injector import containers, providers
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from novelsave.services import FileService, NovelService
from novelsave.services.compilers import EpubCompiler, CompilerProvider
from novelsave.services.source import SourceGatewayProvider
from novelsave.utils.adapters import SourceAdapter, DTOAdapter


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


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
    session = providers.Singleton(Session, engine, future=True)


class Services(containers.DeclarativeContainer):
    data_config = providers.Configuration()

    adapters = providers.DependenciesContainer()
    infrastructure = providers.DependenciesContainer()

    file_service = providers.Factory(
        FileService,
        data_dir=data_config.dir,
        division_rules=data_config.division_rules,
    )

    novel_service = providers.Factory(
        NovelService,
        session=infrastructure.session,
        dto_adapter=adapters.dto_adapter,
        file_service=file_service,
    )

    source_gateway_provider = providers.Factory(
        SourceGatewayProvider,
        source_adapter=adapters.source_adapter,
    )


class Compilers(containers.DeclarativeContainer):
    novel_config = providers.Configuration()
    services = providers.DependenciesContainer()

    epub_compiler = providers.Factory(
        EpubCompiler,
        novels_dir=novel_config.dir,
        novel_service=services.novel_service,
        source_provider=services.source_gateway_provider,
    )

    compiler_provider = providers.Factory(
        CompilerProvider,
        epub=epub_compiler,
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

    compilers = providers.Container(
        Compilers,
        novel_config=config.novel,
        services=services,
    )
