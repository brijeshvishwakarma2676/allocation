from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import TimestampMixin
import enum

class AllocationStatus(str, enum.Enum):
    PRE_ALLOCATED = "pre_allocated"
    COMPETING     = "competing"
    HOLD          = "hold"
    ALLOCATED     = "allocated"
    DISPLACED     = "displaced"

class UnitAllocation(Base, TimestampMixin):
    __tablename__ = "unit_allocations"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    unit_id         = Column(Integer, ForeignKey("units.id"), nullable=False)
    ghng            = Column(String(50), ForeignKey("customers.ghng"), nullable=False)
    status          = Column(Enum(AllocationStatus), default=AllocationStatus.PRE_ALLOCATED)
    hold_expires_at = Column(DateTime, nullable=True)
    assigned_at     = Column(DateTime, nullable=True)
    paid_at         = Column(DateTime, nullable=True)
    easebuzz_txn_id = Column(String(100), nullable=True)

    unit     = relationship("Unit", back_populates="allocations")
    customer = relationship("Customer", back_populates="allocations")
