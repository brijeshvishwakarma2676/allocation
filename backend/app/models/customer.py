from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import TimestampMixin

class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    ghng                 = Column(String(50), primary_key=True)
    name                 = Column(String(255), nullable=True)
    phone                = Column(String(20), nullable=True)
    unit_type_preference = Column(String(20), nullable=True)   # 1BHK, 2BHK etc.

    allocations   = relationship("UnitAllocation", back_populates="customer")
    cancellations = relationship("Cancellation", back_populates="customer")
