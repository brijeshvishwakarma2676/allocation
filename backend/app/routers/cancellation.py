from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.cancellation import Cancellation, CancellationStageLog, CancellationStage, StageAction

router = APIRouter(prefix="/cancellation", tags=["Cancellation"])

STAGE_FLOW = [
    CancellationStage.MANDS_REVIEW,
    CancellationStage.FINANCE_REVIEW,
    CancellationStage.PREAUDIT_REVIEW,
    CancellationStage.BANKING,
    CancellationStage.COMPLETE,
]

class CancelRequest(BaseModel):
    ghng: str
    unit_id: int
    reason: str

class ReviewRequest(BaseModel):
    cancellation_id: int
    action: StageAction
    actor_role: str
    reason: str | None = None
    refund_reference_id: str | None = None

@router.post("/request")
def request_cancellation(req: CancelRequest, db: Session = Depends(get_db)):
    cancellation = Cancellation(
        ghng=req.ghng,
        unit_id=req.unit_id,
        reason=req.reason,
        stage=CancellationStage.MANDS_REVIEW,
    )
    db.add(cancellation)
    db.commit()
    db.refresh(cancellation)
    return {"cancellation_id": cancellation.id, "stage": cancellation.stage}

@router.get("/status/{cancellation_id}")
def get_status(cancellation_id: int, db: Session = Depends(get_db)):
    c = db.query(Cancellation).filter(Cancellation.id == cancellation_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cancellation not found")
    logs = db.query(CancellationStageLog).filter(
        CancellationStageLog.cancellation_id == cancellation_id
    ).order_by(CancellationStageLog.actioned_at).all()
    return {"cancellation_id": c.id, "stage": c.stage, "logs": logs}

@router.post("/review")
def review(req: ReviewRequest, db: Session = Depends(get_db)):
    c = db.query(Cancellation).filter(Cancellation.id == req.cancellation_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cancellation not found")
    if c.stage in [CancellationStage.COMPLETE, CancellationStage.REJECTED]:
        raise HTTPException(status_code=400, detail=f"Already {c.stage}")

    log = CancellationStageLog(
        cancellation_id=c.id,
        stage=c.stage,
        action=req.action,
        actor_role=req.actor_role,
        reason=req.reason,
    )
    db.add(log)

    if req.action == StageAction.REJECTED:
        c.stage = CancellationStage.REJECTED
    else:
        current_idx = STAGE_FLOW.index(c.stage)
        next_stage = STAGE_FLOW[current_idx + 1]
        c.stage = next_stage
        if next_stage == CancellationStage.COMPLETE and req.refund_reference_id:
            c.refund_reference_id = req.refund_reference_id

    db.commit()
    return {"cancellation_id": c.id, "stage": c.stage}
