from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import TimestampMixin
import enum

class UnitStatus(str, enum.Enum):
    AVAILABLE     = "available"
    PRE_ALLOCATED = "pre_allocated"
    HOLD          = "hold"
    COMPETING     = "competing"
    ALLOCATED     = "allocated"
    CANCELLED     = "cancelled"

class Band(str, enum.Enum):
    B1 = "B1"
    B2 = "B2"
    B3 = "B3"
    B4 = "B4"
    B5 = "B5"

class Unit(Base, TimestampMixin):
    __tablename__ = "units"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    tower_id          = Column(Integer, ForeignKey("towers.id"), nullable=False)
    floor             = Column(Integer, nullable=False)
    band              = Column(Enum(Band), nullable=False)
    unit_no           = Column(Integer, nullable=False)
    size_sqft         = Column(Integer, nullable=False)
    status            = Column(Enum(UnitStatus), default=UnitStatus.AVAILABLE)
    allocated_to_ghng = Column(String(50), nullable=True)
    allocated_at      = Column(DateTime, nullable=True)

    tower       = relationship("Tower", back_populates="units")
    allocations = relationship("UnitAllocation", back_populates="unit")
