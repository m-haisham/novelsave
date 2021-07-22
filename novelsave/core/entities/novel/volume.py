from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..model import Model


class Volume(Model):
    __tablename__ = 'volumes'

    id = Column(Integer, primary_key=True)
    index = Column(Integer)
    name = Column(String)

    novel_id = Column(Integer, ForeignKey('novels.id'))
    novel = relationship('Novel', back_populates='volumes')

    chapters = relationship('Chapter', back_populates='volume')