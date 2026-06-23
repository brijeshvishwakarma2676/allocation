"""
seed.py — runs once to prepare the allocation system on top of existing Mavis data.

What it does:
  1. Backfills units.band (currently NULL/double) with the correct band name
     derived from floor_master + band_master (B1–B5).
  2. Ensures the allocation-specific tables exist (create_all already does this in main.py).

What it does NOT do:
  - Does not recreate projects / towers / units (already loaded from Mavis export).
"""

from sqlalchemy import text
from app.database import SessionLocal, engine, Base
from app import models  # ensure all models are imported so create_all sees them


def backfill_unit_bands(db) -> int:
    """
    Set units.band = 'B1'…'B5' based on floor_master → band_master join.

    The column was originally `double` (NULL) from Mavis export.
    We ALTER it to VARCHAR first, then fill.
    """
    # Change column type so we can store string values like 'B1'
    db.execute(text("ALTER TABLE units MODIFY COLUMN band VARCHAR(10) NULL"))
    db.commit()

    result = db.execute(text("""
        UPDATE units u
        JOIN towers t    ON u.tower_id = CONVERT(t.tower_id USING utf8mb4) COLLATE utf8mb4_0900_ai_ci
        JOIN floor_master fm
            ON fm.tower_id = t.id
            AND fm.floor_sequence = u.floor_number
        JOIN band_master bm
            ON bm.id = fm.band_id
        SET u.band = CONCAT('B', SUBSTRING(bm.band_name, 6))
        WHERE u.band IS NULL
          AND u.floor_number IS NOT NULL
    """))
    db.commit()
    return result.rowcount


def seed():
    # Create allocation-specific tables (unit_allocations, customers, cancellations, etc.)
    Base.metadata.create_all(bind=engine)
    print("Allocation tables created / verified.")

    db = SessionLocal()
    try:
        updated = backfill_unit_bands(db)
        print(f"Backfilled band on {updated} units.")

        # Verify
        result = db.execute(text(
            "SELECT band, COUNT(*) as cnt FROM units WHERE band IS NOT NULL GROUP BY band ORDER BY band"
        ))
        for row in result:
            print(f"  {row[0]}: {row[1]} units")

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
