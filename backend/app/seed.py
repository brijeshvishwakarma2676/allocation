from datetime import datetime
from app.database import SessionLocal, engine, Base
from app.models import Project, Tower, Unit
from app.models.unit import Band, UnitStatus

# Create all tables
Base.metadata.create_all(bind=engine)

# Unit sizes per position (1-indexed)
UNIT_SIZES = {1: 322, 2: 322, 3: 621, 4: 484, 5: 322, 6: 322, 7: 484, 8: 621}

TOWER_DATA = [
    # (tower_no, tower_name, preference, sequence, is_active)
    # 1 = active, 0 = inactive (only 1st preference active by default)
    (8,  "Crest",    1, 1,  1),
    (9,  "Triumph",  1, 2,  1),
    (10, "Crown",    1, 3,  1),
    (13, "Prestige", 1, 4,  1),
    (14, "Horizon",  1, 5,  1),
    (15, "Radiance", 1, 6,  1),
    (6,  "Aspire",   1, 7,  1),
    (7,  "Blossom",  1, 8,  1),
    (12, "Pinnacle", 1, 9,  1),
    (16, "Fortune",  2, 10, 0),
    (17, "Bright",   2, 11, 0),
    (18, "Grand",    2, 12, 0),
    (1,  "Dawn",     3, 13, 0),
    (2,  "Aura",     3, 14, 0),
    (3,  "Glory",    3, 15, 0),
    (4,  "Pride",    3, 16, 0),
    (5,  "Grace",    3, 17, 0),
    (11, "Prime",    3, 18, 0),
]

def get_band(floor: int) -> Band:
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

def seed():
    db = SessionLocal()
    now = datetime.utcnow()
    try:
        # Skip if already seeded
        if db.query(Project).filter_by(name="Naigaon Residential").first():
            print("Already seeded. Skipping.")
            return

        # Create project
        project = Project(
            name="Naigaon Residential",
            location="Naigaon, Maharashtra",
            developer="House of Abhinandan Lodha",
            is_active=1,
            created_at=now,
            updated_at=now,
        )
        db.add(project)
        db.flush()
        print(f"Created project: {project.name} (id={project.id})")

        # Create towers and units
        total_units = 0
        for tower_no, tower_name, preference, sequence, is_active in TOWER_DATA:
            tower = Tower(
                project_id=project.id,
                tower_no=tower_no,
                tower_name=tower_name,
                preference=preference,
                sequence=sequence,
                total_floors=35,
                units_per_floor=8,
                is_active=is_active,
                created_at=now,
                updated_at=now,
            )
            db.add(tower)
            db.flush()

            for floor in range(1, 36):
                band = get_band(floor)
                for unit_no in range(1, 9):
                    unit = Unit(
                        tower_id=tower.id,
                        floor=floor,
                        band=band,
                        unit_no=unit_no,
                        size_sqft=UNIT_SIZES[unit_no],
                        status=UnitStatus.AVAILABLE,
                        is_active=1,
                        created_at=now,
                        updated_at=now,
                    )
                    db.add(unit)
                    total_units += 1

            print(f"  Tower {tower_no} ({tower_name}): is_active={is_active} — seeded 280 units")

        db.commit()
        print(f"\nDone. Total units created: {total_units}")

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed()
