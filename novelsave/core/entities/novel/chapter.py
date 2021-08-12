from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship

from ..base import Base


class Chapter(Base):
    __tablename__ = 'chapters'
    __table_args__ = (
        UniqueConstraint('volume_id', 'index', name='volume_index_uc'),
    )

    id = Column(Integer, primary_key=True)
    index = Column(Integer, nullable=False)
    title = Column(String)
    url = Column(String)

    content_path = Column(String, nullable=True)

    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

    volume_id = Column(Integer, ForeignKey('volumes.id'))
    volume = relationship('Volume', back_populates='chapters', lazy='joined')
