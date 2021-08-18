from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from ..base import Base


class Volume(Base):
    __tablename__ = 'volumes'
    __table_args__ = (
        UniqueConstraint('novel_id', 'index'),
    )

    id = Column(Integer, primary_key=True)
    index = Column(Integer, nullable=False)
    name = Column(String, nullable=False)

    novel_id = Column(Integer, ForeignKey('novels.id'), nullable=False)
    novel = relationship('Novel', back_populates='volumes')

    chapters = relationship('Chapter', back_populates='volume', cascade='all, delete-orphan')
