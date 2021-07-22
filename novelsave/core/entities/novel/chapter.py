from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from ..model import Model


class Chapter(Model):
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True)
    index = Column(Integer, unique=True, nullable=False)
    title = Column(String)
    url = Column(String)

    content_path = Column(String, nullable=True)

    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

    volume_id = Column(Integer, ForeignKey('volumes.id'))
    volume = relationship('Volume', back_populates='chapters')
