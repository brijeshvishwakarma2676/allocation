from typing import Optional
from pydantic import BaseModel
from app.models.cancellation import StageAction


class CancelRequest(BaseModel):
    ghng: str
    unit_id: int
    reason: str


class ReviewRequest(BaseModel):
    cancellation_id: int
    action: StageAction
    actor_role: str
    reason: Optional[str] = None
    refund_reference_id: Optional[str] = None
