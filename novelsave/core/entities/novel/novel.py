from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship

from ..base import Base


class Novel(Base):
    __tablename__ = 'novels'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String)
    synopsis = Column(String)
    lang = Column(String)

    thumbnail_url = Column(String)
    thumbnail_path = Column(String)

    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

    urls = relationship('NovelUrl', back_populates='novel', cascade='all, delete-orphan')
    volumes = relationship('Volume', back_populates='novel', cascade='all, delete-orphan')
    novel_metadata = relationship('MetaData', back_populates='novel', cascade='all, delete-orphan')
    assets = relationship('Asset', back_populates='novel', cascade='all, delete-orphan')
