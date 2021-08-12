from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from ..base import Base


class Volume(Base):
    __tablename__ = 'volumes'
    __table_args__ = (
        UniqueConstraint('novel_id', 'index', name='novel_index_uc'),
    )

    id = Column(Integer, primary_key=True)
    index = Column(Integer)
    name = Column(String)

    novel_id = Column(Integer, ForeignKey('novels.id'))
    novel = relationship('Novel', back_populates='volumes')

    chapters = relationship('Chapter', back_populates='volume')
