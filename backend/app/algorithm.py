from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.unit import Unit, UnitStatus, Band
from app.models.unit_allocation import UnitAllocation, AllocationStatus
from app.models.tower import Tower

BAND_ORDER = [Band.B5, Band.B4, Band.B3, Band.B2, Band.B1]
MAX_CUSTOMERS_PER_UNIT = 10

# Maps each band to the floor range (top to bottom for search)
BAND_FLOORS = {
    Band.B5: list(range(35, 28, -1)),   # 35 down to 29
    Band.B4: list(range(28, 21, -1)),   # 28 down to 22
    Band.B3: list(range(21, 14, -1)),   # 21 down to 15
    Band.B2: list(range(14, 7, -1)),    # 14 down to 8  (B2+B1 combined)
    Band.B1: list(range(7, 0, -1)),     # 7 down to 1
}

def get_band_for_floor(floor: int) -> Band:
    if floor >= 29:
        return Band.B5
    elif floor >= 22:
        return Band.B4
    elif floor >= 15:
        return Band.B3
    elif floor >= 8:
        return Band.B2
    else:
        return Band.B1

def get_active_customer_count(db: Session, unit_id: int) -> int:
    return db.query(func.count(UnitAllocation.id)).filter(
        UnitAllocation.unit_id == unit_id,
        UnitAllocation.status.in_([
            AllocationStatus.PRE_ALLOCATED,
            AllocationStatus.COMPETING,
            AllocationStatus.HOLD,
        ])
    ).scalar() or 0

def find_next_available_unit(
    db: Session,
    project_id: int,
    current_tower_sequence: int,
    current_floor: int,
    unit_no: int,
) -> Unit | None:
    """
    Band-drop algorithm:
    1. Drop one band within same tower (B5→B4→B3→B2→B1)
    2. Search top to bottom floor within that band
    3. Search left to right unit (same unit_no type preferred, then any)
    4. If all bands in tower exhausted → move to next tower in sequence (start from B5)
    """
    current_band = get_band_for_floor(current_floor)
    start_band_idx = BAND_ORDER.index(current_band)

    # Get all active towers for this project in sequence order
    towers = (
        db.query(Tower)
        .filter(Tower.project_id == project_id, Tower.is_active == True)
        .order_by(Tower.sequence)
        .all()
    )

    tower_sequences = [t.sequence for t in towers]
    if current_tower_sequence not in tower_sequences:
        return None

    current_tower_idx = tower_sequences.index(current_tower_sequence)

    for tower_idx in range(current_tower_idx, len(towers)):
        tower = towers[tower_idx]
        band_start = start_band_idx + 1 if tower_idx == current_tower_idx else 0

        for band_idx in range(band_start, len(BAND_ORDER)):
            band = BAND_ORDER[band_idx]
            floors = BAND_FLOORS[band]

            for floor in floors:
                # Prefer same unit_no, fallback to any available on that floor
                for preferred_unit_no in [unit_no] + [u for u in range(1, 9) if u != unit_no]:
                    unit = (
                        db.query(Unit)
                        .filter(
                            Unit.tower_id == tower.id,
                            Unit.floor == floor,
                            Unit.unit_no == preferred_unit_no,
                            Unit.status == UnitStatus.AVAILABLE,
                        )
                        .first()
                    )
                    if unit and get_active_customer_count(db, unit.id) < MAX_CUSTOMERS_PER_UNIT:
                        return unit

        # Reset band to B5 for next tower
        start_band_idx = -1

    return None
