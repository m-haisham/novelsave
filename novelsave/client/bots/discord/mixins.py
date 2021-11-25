import shutil

from novelsave import migrations
from novelsave.containers import Application
from novelsave.core.services import (
    BaseNovelService,
    BasePathService,
    BaseAssetService,
    BaseFileService,
)
from novelsave.core.services.packagers import BasePackagerProvider
from novelsave.core.services.source import BaseSourceService
from novelsave.utils.adapters import DTOAdapter
from . import config


class ContainerMixin:
    application: Application
    source_service: BaseSourceService
    novel_service: BaseNovelService
    path_service: BasePathService
    dto_adapter: DTOAdapter
    asset_service: BaseAssetService
    file_service: BaseFileService
    packager_provider: BasePackagerProvider

    @staticmethod
    def _make_unique_config(id_: str):
        temp: dict = config.app()

        config_dir = temp["config"]["dir"] / "discord" / id_
        schema, url = temp["infrastructure"]["database"]["url"].split(
            ":///", maxsplit=1
        )

        temp.update(
            {
                "config": {
                    "dir": config_dir,
                    "file": config_dir / temp["config"]["file"].name,
                },
                "novel": {
                    "dir": config_dir / "novels",
                },
                "data": {
                    "dir": config_dir / "data",
                },
                "infrastructure": {
                    "database": {
                        "url": f"{schema}:///{str(config_dir / 'data.sqlite')}",
                    },
                },
            }
        )

        shutil.rmtree(config_dir, ignore_errors=True)
        config_dir.mkdir(parents=True, exist_ok=True)

        return temp

    def setup_container(self, id_: str):
        self.application = Application()
        self.application.config.from_dict(self._make_unique_config(id_))

        # acquire services
        self.source_service = self.application.services.source_service()
        self.novel_service = self.application.services.novel_service()
        self.path_service = self.application.services.path_service()
        self.dto_adapter = self.application.adapters.dto_adapter()
        self.asset_service = self.application.services.asset_service()
        self.file_service = self.application.services.file_service()
        self.packager_provider = self.application.packagers.packager_provider()

        # migrate database to latest schema
        migrations.migrate(self.application.config.get("infrastructure.database.url"))

    def close_session(self):
        self.application.infrastructure.session().close()
        self.application.infrastructure.session_factory().close_all()
        self.application.infrastructure.engine().dispose()
