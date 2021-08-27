from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship, backref

from ..base import Base


class Chapter(Base):
    __tablename__ = 'chapters'
    __table_args__ = (
        UniqueConstraint('volume_id', 'index'),
    )

    id = Column(Integer, primary_key=True)
    index = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)

    content = Column(String, nullable=True)
    volume_id = Column(Integer, ForeignKey('volumes.id'), nullable=False)
    volume = relationship('Volume', back_populates='chapters')

    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())
