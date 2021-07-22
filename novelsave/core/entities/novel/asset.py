from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..model import Model


class Asset(Model):
    __tablename__ = 'assets'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    hash = Column(String)

    novel_id = Column(Integer, ForeignKey('novels.id'))
    novel = relationship('Novel', back_populates='assets')
