from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Tower, Unit, Customer
from app.models.unit_allocation import UnitAllocation, AllocationStatus
from app.algorithm import BAND_ORDER, BAND_FLOORS
from app.schemas.admin import EnablePreferenceRequest, AssignUnitRequest

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/enable-towers")
def enable_towers(req: EnablePreferenceRequest, db: Session = Depends(get_db)):
    """
    Activate towers for a project by setting is_active=1.
    preference field maps to tower groups the admin wants to open.
    group 2/3 = towers that currently have is_active=0 and no sequence.
    """
    towers = db.query(Tower).filter(
        Tower.project_id == req.project_id,
        Tower.is_active == 0,
    ).all()
    if not towers:
        raise HTTPException(status_code=404, detail="No inactive towers found for this project")

    # Enable the next N inactive towers (preference=2 → next 9, preference=3 → remaining)
    batch_size = 9
    to_enable = towers[:batch_size]
    next_seq = (
        db.query(Tower)
        .filter(Tower.project_id == req.project_id, Tower.tower_sequence.isnot(None))
        .count()
    ) + 1
    for t in to_enable:
        t.is_active = 1
        t.tower_sequence = next_seq
        next_seq += 1

    db.commit()
    return {"enabled": len(to_enable), "group": req.preference}


@router.post("/assign-unit")
def assign_unit(req: AssignUnitRequest, db: Session = Depends(get_db)):
    """Manually pre-allocate a GHNG number to a specific unit (admin override)."""
    unit = db.query(Unit).filter(Unit.id == req.unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    if unit.status == "Booked":
        raise HTTPException(status_code=409, detail="Unit already booked")

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

    db.commit()
    return {"success": True, "unit_id": req.unit_id, "ghng": req.ghng}


@router.get("/dashboard/{project_id}")
def dashboard(project_id: str, db: Session = Depends(get_db)):
    """
    Real-time allocation state per tower.
    project_id is the Mavis string ID (e.g. "project-1728380099837").
    """
    towers = (
        db.query(Tower)
        .filter(Tower.project_id == project_id)
        .order_by(Tower.tower_sequence.nullslast(), Tower.id)
        .all()
    )
    result = []
    for tower in towers:
        units = db.query(Unit).filter(Unit.tower_id == tower.tower_id).all()
        booked    = sum(1 for u in units if u.status == "Booked")
        available = sum(1 for u in units if u.status == "Available")
        competing = db.query(UnitAllocation).join(Unit, UnitAllocation.unit_id == Unit.id).filter(
            Unit.tower_id == tower.tower_id,
            UnitAllocation.status.in_([AllocationStatus.COMPETING, AllocationStatus.HOLD]),
        ).count()
        result.append({
            "tower_id":       tower.id,
            "tower_ext_id":   tower.tower_id,
            "tower_name":     tower.tower_name,
            "tower_sequence": tower.tower_sequence,
            "no_of_floors":   tower.no_of_floors,
            "is_active":      tower.is_active,
            "total_units":    len(units),
            "booked":         booked,
            "competing":      competing,
            "available":      available,
        })
    return result


@router.get("/band-config/{project_id}")
def band_config(project_id: str, db: Session = Depends(get_db)):
    """
    Per-tower band configuration: which unit IDs fall in each band.
    Mirrors the BandMaster data with live unit availability stats.
    """
    towers = (
        db.query(Tower)
        .filter(Tower.project_id == project_id)
        .order_by(Tower.tower_sequence.nullslast(), Tower.id)
        .all()
    )
    result = []
    for tower in towers:
        all_units = (
            db.query(Unit)
            .filter(Unit.tower_id == tower.tower_id)
            .order_by(Unit.floor_number.desc(), Unit.unit_no)
            .all()
        )
        # Group by band derived from floor_number
        from app.algorithm import get_band_for_floor
        by_band: dict[str, list[Unit]] = {b: [] for b in BAND_ORDER}
        for u in all_units:
            if u.floor_number:
                by_band[get_band_for_floor(u.floor_number)].append(u)

        band_config_lists = [[u.id for u in by_band[b]] for b in BAND_ORDER]
        band_summary = {}
        for b in BAND_ORDER:
            units_in_band = by_band[b]
            floors = [u.floor_number for u in units_in_band if u.floor_number]
            band_summary[b] = {
                "total":       len(units_in_band),
                "floor_range": f"{min(floors)}–{max(floors)}" if floors else "N/A",
                "available":   sum(1 for u in units_in_band if u.status == "Available"),
                "booked":      sum(1 for u in units_in_band if u.status == "Booked"),
            }

        result.append({
            "tower_id":       tower.id,
            "tower_ext_id":   tower.tower_id,
            "tower_name":     tower.tower_name,
            "tower_sequence": tower.tower_sequence,
            "is_active":      tower.is_active,
            "band_order":     BAND_ORDER,
            "band_config":    band_config_lists,
            "band_summary":   band_summary,
        })
    return result
