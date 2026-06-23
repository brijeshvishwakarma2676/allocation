from sqlalchemy import Column, Integer, BigInteger, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Unit(Base):
    """Read-only reference to the Mavis units table. Not created by create_all."""
    __tablename__ = "units"
    __table_args__ = {"extend_existing": True}

    id           = Column(Integer, primary_key=True)
    unit_no      = Column(BigInteger)   # composite: floor*100 + position, e.g. 2908
    unit_name    = Column(Text)         # e.g. "HoABL T8 - 1 BHK - 2908"
    tower_id     = Column(Text)         # Mavis string, e.g. "tower-1757934355725"
    tower_name   = Column(Text)
    floor_number = Column(BigInteger)   # physical floor 1–35
    typology_id  = Column(Text)         # Mavis typology string ID
    basic_price  = Column(BigInteger)
    facing       = Column(Text)
    band         = Column(String(10))   # "B1"–"B5" (backfilled from floor_master)
    status       = Column(Text)         # "Available" | "Booked"

    allocations = relationship("UnitAllocation", back_populates="unit")
