from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class InfrastructureContainer(containers.DeclarativeContainer):

    database_url = providers.Dependency()

    engine = providers.Singleton(create_engine, url=database_url, future=True)
    session = providers.Singleton(sessionmaker, bind=engine, future=True)
