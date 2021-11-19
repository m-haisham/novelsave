from dependency_injector import containers, providers


class DiscordApplication(containers.DeclarativeContainer):
    config = providers.Configuration(strict=True)
