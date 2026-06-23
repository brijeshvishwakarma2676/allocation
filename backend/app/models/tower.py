from sqlalchemy import Column, Integer, String, SmallInteger
from app.database import Base


class Tower(Base):
    """Read-only reference to the Mavis towers table. Not created by create_all."""
    __tablename__ = "towers"
    __table_args__ = {"extend_existing": True}

    id             = Column(Integer, primary_key=True)
    tower_id       = Column(String(255))   # Mavis string ID, e.g. "tower-1757934355725"
    tower_name     = Column(String(255))
    project_id     = Column(String(255))   # Mavis project string ID
    tower_sequence = Column(Integer)       # allocation priority order (1 = first)
    no_of_floors   = Column(Integer)
    is_active      = Column(SmallInteger)
