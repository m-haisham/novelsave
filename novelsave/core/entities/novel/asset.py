from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from ..base import Base


class Asset(Base):
    __tablename__ = 'assets'
    __table_args__ = (
        UniqueConstraint('novel_id', 'url'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    url = Column(String)
    path = Column(String)

    type_id = Column(Integer, ForeignKey('asset_types.id'), nullable=False)
    type = relationship('AssetType', back_populates='assets')

    novel_id = Column(Integer, ForeignKey('novels.id'), nullable=False)
    novel = relationship('Novel', back_populates='assets')
