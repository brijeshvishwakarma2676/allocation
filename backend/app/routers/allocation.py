from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Customer
from app.models.unit import Unit
from app.models.tower import Tower
from app.models.unit_allocation import UnitAllocation, AllocationStatus
from app.algorithm import find_next_available_unit, get_band_for_floor
from app.schemas.allocation import PreAllocateRequest, PayRequest

router = APIRouter(prefix="/allocation", tags=["Allocation"])

HOLD_MINUTES = 30


@router.post("/pre-allocate")
def pre_allocate(req: PreAllocateRequest, db: Session = Depends(get_db)):
    """Bulk assign up to 3 GHNG customers per unit before Allocation Day."""
    created = 0
    for mapping in req.mappings:
        ghng = mapping["ghng"]
        unit_id = mapping["unit_id"]

        unit = db.query(Unit).filter(Unit.id == unit_id).first()
        if not unit:
            continue

        customer = db.query(Customer).filter(Customer.ghng == ghng).first()
        if not customer:
            customer = Customer(ghng=ghng)
            db.add(customer)
            db.flush()

        existing = db.query(UnitAllocation).filter(
            UnitAllocation.unit_id == unit_id,
            UnitAllocation.ghng == ghng,
        ).first()
        if existing:
            continue

        count = db.query(func.count(UnitAllocation.id)).filter(
            UnitAllocation.unit_id == unit_id,
            UnitAllocation.status == AllocationStatus.PRE_ALLOCATED,
        ).scalar()
        if count >= 3:
            continue

        db.add(UnitAllocation(unit_id=unit_id, ghng=ghng, status=AllocationStatus.PRE_ALLOCATED))
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
    if not unit:
        raise HTTPException(status_code=404, detail="Unit record not found")

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
        "unit_id":             unit.id,
        "unit_no":             unit.unit_no,
        "unit_name":           unit.unit_name,
        "tower_id":            unit.tower_id,
        "tower_name":          unit.tower_name,
        "floor":               unit.floor_number,
        "band":                get_band_for_floor(unit.floor_number) if unit.floor_number else None,
        "typology_id":         unit.typology_id,
        "basic_price":         unit.basic_price,
        "facing":              unit.facing,
        "status":              alloc.status,
        "hold_expires_at":     alloc.hold_expires_at,
        "competing_customers": competitors,
    }


@router.post("/pay")
def pay(req: PayRequest, db: Session = Depends(get_db)):
    """Customer confirms payment — locks unit atomically, band-drops all displaced customers."""
    unit = db.query(Unit).filter(Unit.id == req.unit_id).with_for_update().first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    tower = db.query(Tower).filter(Tower.tower_id == unit.tower_id).first()
    if not tower:
        raise HTTPException(status_code=404, detail="Tower not found")

    if unit.status == "Booked":
        # Unit already taken — band-drop this customer to next available
        next_unit = find_next_available_unit(
            db=db,
            project_id=tower.project_id,
            current_tower_sequence=tower.tower_sequence,
            current_floor=unit.floor_number,
            current_unit_no=unit.unit_no,
        )
        if not next_unit:
            raise HTTPException(status_code=410, detail="No units available")

        alloc = db.query(UnitAllocation).filter(
            UnitAllocation.unit_id == req.unit_id,
            UnitAllocation.ghng == req.ghng,
        ).first()
        if alloc:
            alloc.unit_id        = next_unit.id
            alloc.status         = AllocationStatus.HOLD
            alloc.hold_expires_at = datetime.utcnow() + timedelta(minutes=HOLD_MINUTES)
            alloc.assigned_at    = datetime.utcnow()

        db.commit()
        return {
            "success":         False,
            "message":         "Unit already taken. Moved to next available.",
            "next_unit_id":    next_unit.id,
            "next_unit_no":    next_unit.unit_no,
            "next_unit_name":  next_unit.unit_name,
            "hold_expires_at": alloc.hold_expires_at if alloc else None,
        }

    # Lock unit for this customer
    alloc = db.query(UnitAllocation).filter(
        UnitAllocation.unit_id == req.unit_id,
        UnitAllocation.ghng == req.ghng,
    ).first()
    if not alloc:
        raise HTTPException(status_code=403, detail="Not pre-allocated to this unit")

    alloc.status         = AllocationStatus.ALLOCATED
    alloc.paid_at        = datetime.utcnow()
    alloc.easebuzz_txn_id = req.easebuzz_txn_id

    unit.status = "Booked"

    # Band-drop every other customer on this unit
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
        next_unit = find_next_available_unit(
            db=db,
            project_id=tower.project_id,
            current_tower_sequence=tower.tower_sequence,
            current_floor=unit.floor_number,
            current_unit_no=unit.unit_no,
        )
        if next_unit:
            other.unit_id         = next_unit.id
            other.status          = AllocationStatus.HOLD
            other.hold_expires_at = datetime.utcnow() + timedelta(minutes=HOLD_MINUTES)
            other.assigned_at     = datetime.utcnow()
        else:
            other.status = AllocationStatus.DISPLACED

    db.commit()
    return {"success": True, "allocated_unit_id": req.unit_id, "unit_no": unit.unit_no}
