from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Customer
from app.models.unit import Unit, UnitStatus
from app.models.unit_allocation import UnitAllocation, AllocationStatus
from app.algorithm import find_next_available_unit, get_band_for_floor

router = APIRouter(prefix="/allocation", tags=["Allocation"])

HOLD_MINUTES = 30

class PreAllocateRequest(BaseModel):
    project_id: int
    mappings: list[dict]   # [{"ghng": "GHNG001", "unit_id": 123}, ...]

class PayRequest(BaseModel):
    ghng: str
    unit_id: int
    easebuzz_txn_id: str

@router.post("/pre-allocate")
def pre_allocate(req: PreAllocateRequest, db: Session = Depends(get_db)):
    """Bulk assign 3 customers per unit before Allocation Day."""
    created = 0
    for mapping in req.mappings:
        ghng = mapping["ghng"]
        unit_id = mapping["unit_id"]

        unit = db.query(Unit).filter(Unit.id == unit_id).first()
        if not unit:
            continue

        # Ensure customer exists
        customer = db.query(Customer).filter(Customer.ghng == ghng).first()
        if not customer:
            customer = Customer(ghng=ghng)
            db.add(customer)
            db.flush()

        # Check not already assigned
        existing = db.query(UnitAllocation).filter(
            UnitAllocation.unit_id == unit_id,
            UnitAllocation.ghng == ghng,
        ).first()
        if existing:
            continue

        # Cap at 3 pre-allocations per unit
        count = db.query(func.count(UnitAllocation.id)).filter(
            UnitAllocation.unit_id == unit_id,
            UnitAllocation.status == AllocationStatus.PRE_ALLOCATED,
        ).scalar()
        if count >= 3:
            continue

        db.add(UnitAllocation(unit_id=unit_id, ghng=ghng, status=AllocationStatus.PRE_ALLOCATED))
        unit.status = UnitStatus.PRE_ALLOCATED
        created += 1

    db.commit()
    return {"assigned": created}

@router.get("/my-unit/{ghng}")
def my_unit(ghng: str, db: Session = Depends(get_db)):
    """Return the current unit assigned or held for this customer."""
    alloc = (
        db.query(UnitAllocation)
        .filter(
            UnitAllocation.ghng == ghng,
            UnitAllocation.status.in_([
                AllocationStatus.PRE_ALLOCATED,
                AllocationStatus.HOLD,
                AllocationStatus.COMPETING,
            ]),
        )
        .order_by(UnitAllocation.assigned_at.desc())
        .first()
    )
    if not alloc:
        raise HTTPException(status_code=404, detail="No unit currently assigned")

    unit = alloc.unit
    competitors = db.query(func.count(UnitAllocation.id)).filter(
        UnitAllocation.unit_id == unit.id,
        UnitAllocation.ghng != ghng,
        UnitAllocation.status.in_([
            AllocationStatus.PRE_ALLOCATED,
            AllocationStatus.COMPETING,
            AllocationStatus.HOLD,
        ]),
    ).scalar()

    return {
        "unit_id": unit.id,
        "tower_id": unit.tower_id,
        "floor": unit.floor,
        "band": unit.band,
        "unit_no": unit.unit_no,
        "size_sqft": unit.size_sqft,
        "status": alloc.status,
        "hold_expires_at": alloc.hold_expires_at,
        "competing_customers": competitors,
    }

@router.post("/pay")
def pay(req: PayRequest, db: Session = Depends(get_db)):
    """Customer pays for their unit — locks it atomically."""
    unit = db.query(Unit).filter(Unit.id == req.unit_id).with_for_update().first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    if unit.status == UnitStatus.ALLOCATED:
        # Unit already taken — find next available
        tower = unit.tower
        next_unit = find_next_available_unit(
            db=db,
            project_id=tower.project_id,
            current_tower_sequence=tower.sequence,
            current_floor=unit.floor,
            unit_no=unit.unit_no,
        )
        if not next_unit:
            raise HTTPException(status_code=410, detail="No units available")

        # Hold the next unit
        alloc = db.query(UnitAllocation).filter(
            UnitAllocation.unit_id == req.unit_id,
            UnitAllocation.ghng == req.ghng,
        ).first()
        if alloc:
            alloc.unit_id = next_unit.id
            alloc.status = AllocationStatus.HOLD
            alloc.hold_expires_at = datetime.utcnow() + timedelta(minutes=HOLD_MINUTES)
            alloc.assigned_at = datetime.utcnow()

        db.commit()
        return {
            "success": False,
            "message": "Unit already taken. Moved to next available.",
            "next_unit_id": next_unit.id,
            "hold_expires_at": alloc.hold_expires_at if alloc else None,
        }

    # Lock the unit for this customer
    alloc = db.query(UnitAllocation).filter(
        UnitAllocation.unit_id == req.unit_id,
        UnitAllocation.ghng == req.ghng,
    ).first()
    if not alloc:
        raise HTTPException(status_code=403, detail="Not pre-allocated to this unit")

    alloc.status = AllocationStatus.ALLOCATED
    alloc.paid_at = datetime.utcnow()
    alloc.easebuzz_txn_id = req.easebuzz_txn_id

    unit.status = UnitStatus.ALLOCATED
    unit.allocated_to_ghng = req.ghng
    unit.allocated_at = datetime.utcnow()

    # Displace all other customers on this unit
    others = db.query(UnitAllocation).filter(
        UnitAllocation.unit_id == req.unit_id,
        UnitAllocation.ghng != req.ghng,
        UnitAllocation.status.in_([
            AllocationStatus.PRE_ALLOCATED,
            AllocationStatus.COMPETING,
            AllocationStatus.HOLD,
        ]),
    ).all()

    for other in others:
        other_unit = unit
        next_unit = find_next_available_unit(
            db=db,
            project_id=other_unit.tower.project_id,
            current_tower_sequence=other_unit.tower.sequence,
            current_floor=other_unit.floor,
            unit_no=other_unit.unit_no,
        )
        if next_unit:
            other.unit_id = next_unit.id
            other.status = AllocationStatus.HOLD
            other.hold_expires_at = datetime.utcnow() + timedelta(minutes=HOLD_MINUTES)
            other.assigned_at = datetime.utcnow()
        else:
            other.status = AllocationStatus.DISPLACED

    db.commit()
    return {"success": True, "allocated_unit_id": req.unit_id}
