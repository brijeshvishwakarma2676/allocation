from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.unit import Unit
from app.models.unit_allocation import UnitAllocation, AllocationStatus
from app.models.tower import Tower

# Allocation drop order: B5 (top, premium) → B1 (bottom)
BAND_ORDER = ["B5", "B4", "B3", "B2", "B1"]

MAX_CUSTOMERS_PER_UNIT = 10

# Actual floor ranges per band (from floor_master / band_master data)
#   B5: floors 29–35  (7 floors, top)
#   B4: floors 21–28  (8 floors)
#   B3: floors 15–20  (6 floors)
#   B2: floors  8–14  (7 floors)
#   B1: floors  1–7   (7 floors, bottom)
BAND_FLOORS: dict[str, list[int]] = {
    "B5": list(range(35, 28, -1)),   # [35, 34, 33, 32, 31, 30, 29]
    "B4": list(range(28, 20, -1)),   # [28, 27, 26, 25, 24, 23, 22, 21]
    "B3": list(range(20, 14, -1)),   # [20, 19, 18, 17, 16, 15]
    "B2": list(range(14, 7, -1)),    # [14, 13, 12, 11, 10, 9, 8]
    "B1": list(range(7, 0, -1)),     # [7, 6, 5, 4, 3, 2, 1]
}


def get_band_for_floor(floor: int) -> str:
    if floor >= 29:   return "B5"
    elif floor >= 21: return "B4"
    elif floor >= 15: return "B3"
    elif floor >= 8:  return "B2"
    else:             return "B1"


def get_active_customer_count(db: Session, unit_id: int) -> int:
    return db.query(func.count(UnitAllocation.id)).filter(
        UnitAllocation.unit_id == unit_id,
        UnitAllocation.status.in_([
            AllocationStatus.PRE_ALLOCATED,
            AllocationStatus.COMPETING,
            AllocationStatus.HOLD,
        ])
    ).scalar() or 0


def _unit_position(unit_no: int) -> int:
    """Extract the within-floor position from a composite unit number (floor*100 + pos)."""
    return unit_no % 100


def find_next_available_unit(
    db: Session,
    project_id: str,            # Mavis string project ID e.g. "project-1728380099837"
    current_tower_sequence: int,
    current_floor: int,
    current_unit_no: int,       # composite e.g. 2908
) -> Unit | None:
    """
    Band-drop algorithm:
    1. Stay in same tower, drop one band (B5→B4→B3→B2→B1)
    2. Within band: top floor first, left unit (same position) preferred
    3. If all bands in tower exhausted → next tower in sequence, start from B5
    """
    current_band = get_band_for_floor(current_floor)
    current_position = _unit_position(current_unit_no)
    start_band_idx = BAND_ORDER.index(current_band)

    # Active towers for this project, ordered by allocation sequence
    towers = (
        db.query(Tower)
        .filter(
            Tower.project_id == project_id,
            Tower.is_active == 1,
            Tower.tower_sequence.isnot(None),
        )
        .order_by(Tower.tower_sequence)
        .all()
    )

    tower_sequences = [t.tower_sequence for t in towers]
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
                # Preferred position first, then any other position (1–8)
                positions = [current_position] + [p for p in range(1, 9) if p != current_position]
                for pos in positions:
                    target_unit_no = floor * 100 + pos
                    unit = (
                        db.query(Unit)
                        .filter(
                            Unit.tower_id == tower.tower_id,
                            Unit.floor_number == floor,
                            Unit.unit_no == target_unit_no,
                            Unit.status == "Available",
                        )
                        .first()
                    )
                    if unit and get_active_customer_count(db, unit.id) < MAX_CUSTOMERS_PER_UNIT:
                        return unit

        # Reset to B5 for next tower
        start_band_idx = -1

    return None
