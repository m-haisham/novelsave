from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..model import Model


class Source(Model):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    urls = relationship('SourceUrl', back_populates='source')
    novels = relationship('Novel', back_populates='source')
