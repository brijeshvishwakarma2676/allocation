from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import Tower

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    rows = db.execute(text(
        "SELECT id, name, project_id, project_code, developer_name, maharera_number, "
        "launch_start_date, no_of_units, no_of_towers, is_active "
        "FROM projects WHERE is_active = 1 AND deleted_at IS NULL"
    )).mappings().all()
    return [dict(r) for r in rows]


@router.get("/{project_id}/towers")
def list_towers(project_id: int, db: Session = Depends(get_db)):
    project = db.execute(
        text("SELECT id, project_id FROM projects WHERE id = :id"), {"id": project_id}
    ).mappings().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    towers = (
        db.query(Tower)
        .filter(Tower.project_id == project["project_id"])
        .order_by(Tower.tower_sequence.nullslast(), Tower.id)
        .all()
    )
    if not towers:
        raise HTTPException(status_code=404, detail="No towers found")
    return towers
