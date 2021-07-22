from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..model import Model


class SourceUrl(Model):
    __tablename__ = 'source_urls'

    id = Column(Integer, primary_key=True)
    base_url = Column(String, nullable=False)

    source_id = Column(Integer, ForeignKey('sources.id'))
    source = relationship('Source', back_populates='urls')
