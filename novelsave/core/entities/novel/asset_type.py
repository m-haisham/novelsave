from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..base import Base


class AssetType(Base):
    __tablename__ = 'asset_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)

    assets = relationship('Asset', back_populates='type')


