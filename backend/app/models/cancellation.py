from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import TimestampMixin
import enum

class CancellationStage(str, enum.Enum):
    MANDS_REVIEW    = "mands_review"
    FINANCE_REVIEW  = "finance_review"
    PREAUDIT_REVIEW = "preaudit_review"
    BANKING         = "banking"
    COMPLETE        = "complete"
    REJECTED        = "rejected"

class StageAction(str, enum.Enum):
    APPROVED = "approved"
    REJECTED = "rejected"

class Cancellation(Base, TimestampMixin):
    __tablename__ = "cancellations"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    ghng                = Column(String(50), ForeignKey("customers.ghng"), nullable=False)
    unit_id             = Column(Integer, ForeignKey("units.id"), nullable=False)
    reason              = Column(Text, nullable=True)
    stage               = Column(Enum(CancellationStage), default=CancellationStage.MANDS_REVIEW)
    refund_reference_id = Column(String(100), nullable=True)

    customer   = relationship("Customer", back_populates="cancellations")
    stage_logs = relationship("CancellationStageLog", back_populates="cancellation")

class CancellationStageLog(Base, TimestampMixin):
    __tablename__ = "cancellation_stage_logs"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    cancellation_id = Column(Integer, ForeignKey("cancellations.id"), nullable=False)
    stage           = Column(Enum(CancellationStage), nullable=False)
    action          = Column(Enum(StageAction), nullable=False)
    actor_role      = Column(String(50), nullable=False)
    reason          = Column(Text, nullable=True)

    cancellation = relationship("Cancellation", back_populates="stage_logs")
