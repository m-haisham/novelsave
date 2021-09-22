from dependency_injector import containers, providers
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from novelsave.services import FileService, NovelService, PathService, AssetService, MetaService, CalibreService
from novelsave.services.packagers import EpubPackager, HtmlPackager, MobiPackager, PackagerProvider, PdfPackager, \
    Azw3Packager
from novelsave.services.config import ConfigService
from novelsave.services.source import SourceService
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
    config = providers.Configuration()

    adapters = providers.DependenciesContainer()
    infrastructure = providers.DependenciesContainer()

    config_service = providers.Singleton(
        ConfigService,
        config_file=config.config.file,
        default_novel_dir=config.novel.dir,
    )

    meta_service = providers.Factory(
        MetaService,
    )

    file_service = providers.Factory(
        FileService,
    )

    novel_service = providers.Factory(
        NovelService,
        session=infrastructure.session,
        dto_adapter=adapters.dto_adapter,
        file_service=file_service,
    )

    source_service = providers.Singleton(
        SourceService,
        source_adapter=adapters.source_adapter,
    )

    path_service = providers.Factory(
        PathService,
        data_dir=config.data.dir,
        novels_dir=config.novel.dir,
        division_rules=config.data.division_rules,
        novel_service=novel_service,
        source_service=source_service,
    )

    asset_service = providers.Factory(
        AssetService,
        session=infrastructure.session,
        path_service=path_service,
    )

    calibre_service = providers.Factory(CalibreService)


class Packagers(containers.DeclarativeContainer):
    config = providers.Configuration()
    services = providers.DependenciesContainer()

    epub_packager = providers.Factory(
        EpubPackager,
        novel_service=services.novel_service,
        file_service=services.file_service,
        path_service=services.path_service,
        asset_service=services.asset_service,
    )

    html_packager = providers.Factory(
        HtmlPackager,
        static_dir=config.static.dir,
        novel_service=services.novel_service,
        file_service=services.file_service,
        path_service=services.path_service,
        asset_service=services.asset_service,
    )

    mobi_packager = providers.Factory(
        MobiPackager,
        calibre_service=services.calibre_service,
        path_service=services.path_service,
    )

    pdf_packager = providers.Factory(
        PdfPackager,
        calibre_service=services.calibre_service,
        path_service=services.path_service,
    )

    azw3_packager = providers.Factory(
        Azw3Packager,
        calibre_service=services.calibre_service,
        path_service=services.path_service,
    )

    packager_provider = providers.Factory(
        PackagerProvider,
        epub_packager, html_packager, mobi_packager, pdf_packager,
        azw3_packager,
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
        config=config,
        adapters=adapters,
        infrastructure=infrastructure,
    )

    packagers = providers.Container(
        Packagers,
        config=config,
        services=services,
    )
