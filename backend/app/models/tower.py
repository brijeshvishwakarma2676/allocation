from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import TimestampMixin

class Tower(Base, TimestampMixin):
    __tablename__ = "towers"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    project_id      = Column(Integer, ForeignKey("projects.id"), nullable=False)
    tower_no        = Column(Integer, nullable=False)
    tower_name      = Column(String(100), nullable=False)
    preference      = Column(Integer, nullable=False)   # 1, 2, or 3
    sequence        = Column(Integer, nullable=False)   # 1–18 global order
    total_floors    = Column(Integer, default=35)
    units_per_floor = Column(Integer, default=8)

    project = relationship("Project", back_populates="towers")
    units   = relationship("Unit", back_populates="tower")
