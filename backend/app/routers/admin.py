from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from app.database import get_db
from app.models import Tower, Unit, Customer
from app.models.unit import UnitStatus
from app.models.unit_allocation import UnitAllocation, AllocationStatus

router = APIRouter(prefix="/admin", tags=["Admin"])

class EnablePreferenceRequest(BaseModel):
    project_id: int
    preference: int   # 2 or 3

class AssignUnitRequest(BaseModel):
    ghng: str
    unit_id: int

@router.post("/enable-preference")
def enable_preference(req: EnablePreferenceRequest, db: Session = Depends(get_db)):
    """Open 2nd or 3rd preference towers."""
    towers = db.query(Tower).filter(
        Tower.project_id == req.project_id,
        Tower.preference == req.preference,
    ).all()
    if not towers:
        raise HTTPException(status_code=404, detail="No towers found for this preference")
    for t in towers:
        t.is_active = True
    db.commit()
    return {"enabled": len(towers), "preference": req.preference}

@router.post("/assign-unit")
def assign_unit(req: AssignUnitRequest, db: Session = Depends(get_db)):
    """Manually assign a GHNG number to a specific unit."""
    unit = db.query(Unit).filter(Unit.id == req.unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    if unit.status == UnitStatus.ALLOCATED:
        raise HTTPException(status_code=409, detail="Unit already allocated")

    customer = db.query(Customer).filter(Customer.ghng == req.ghng).first()
    if not customer:
        customer = Customer(ghng=req.ghng)
        db.add(customer)
        db.flush()

    existing = db.query(UnitAllocation).filter(
        UnitAllocation.unit_id == req.unit_id,
        UnitAllocation.ghng == req.ghng,
    ).first()
    if not existing:
        db.add(UnitAllocation(
            unit_id=req.unit_id,
            ghng=req.ghng,
            status=AllocationStatus.PRE_ALLOCATED,
        ))
        if unit.status == UnitStatus.AVAILABLE:
            unit.status = UnitStatus.PRE_ALLOCATED

    db.commit()
    return {"success": True, "unit_id": req.unit_id, "ghng": req.ghng}

@router.get("/dashboard/{project_id}")
def dashboard(project_id: int, db: Session = Depends(get_db)):
    """Real-time allocation state per tower."""
    towers = db.query(Tower).filter(Tower.project_id == project_id).order_by(Tower.sequence).all()
    result = []
    for tower in towers:
        units = db.query(Unit).filter(Unit.tower_id == tower.id).all()
        allocated = sum(1 for u in units if u.status == UnitStatus.ALLOCATED)
        available = sum(1 for u in units if u.status == UnitStatus.AVAILABLE)
        competing = sum(1 for u in units if u.status == UnitStatus.COMPETING)
        result.append({
            "tower_id": tower.id,
            "tower_no": tower.tower_no,
            "tower_name": tower.tower_name,
            "preference": tower.preference,
            "sequence": tower.sequence,
            "is_active": tower.is_active,
            "total_units": len(units),
            "allocated": allocated,
            "competing": competing,
            "available": available,
        })
    return result
