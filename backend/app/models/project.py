from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import TimestampMixin

class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    name      = Column(String(255), nullable=False)
    location  = Column(String(255), nullable=True)
    developer = Column(String(255), nullable=True)

    towers = relationship("Tower", back_populates="project")
