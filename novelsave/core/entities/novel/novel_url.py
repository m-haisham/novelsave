from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..base import Base


class NovelUrl(Base):
    __tablename__ = 'novel_urls'

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)

    novel_id = Column(Integer, ForeignKey('novels.id'))
    novel = relationship('Novel', back_populates='urls', lazy='joined')
