from dependency_injector import containers, providers

from .infrastructure import InfrastructureContainer


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration(strict=True)

    infrastructure = InfrastructureContainer(
        database_url=config.database_url(),
    )
