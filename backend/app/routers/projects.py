from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, Tower

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).filter(Project.is_active == True).all()

@router.get("/{project_id}/towers")
def list_towers(project_id: int, db: Session = Depends(get_db)):
    towers = (
        db.query(Tower)
        .filter(Tower.project_id == project_id)
        .order_by(Tower.sequence)
        .all()
    )
    if not towers:
        raise HTTPException(status_code=404, detail="No towers found for this project")
    return towers
