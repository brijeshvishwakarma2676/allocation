from sqlalchemy import Column, Boolean, DateTime, func

class TimestampMixin:
    is_active  = Column(Boolean, default=True, nullable=False)   # 1=active, 0=inactive
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
