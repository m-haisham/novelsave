from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship

from ..model import Model


class Novel(Model):
    __tablename__ = 'novels'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    synopsis = Column(String)

    thumbnail_url = Column(String)
    thumbnail_path = Column(String)

    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

    urls = relationship('NovelUrl', back_populates='novel')

    source_id = Column(Integer, ForeignKey('sources.id'))
    source = relationship('Source', back_populates='novels')

    volumes = relationship('Volume', back_populates='novel')
    assets = relationship('Asset', back_populates='novel')
