from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.customer import Customer
from app.models.unit_allocation import UnitAllocation, AllocationStatus
from app.schemas.customer import CustomerCreate, CustomerBulkCreate

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/")
def list_customers(
    search: Optional[str] = Query(None, description="Search by GHNG, name, or phone"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Customer).filter(Customer.is_active == 1)

    if search:
        like = f"%{search}%"
        q = q.filter(
            Customer.ghng.like(like)
            | Customer.name.like(like)
            | Customer.phone.like(like)
        )

    total = q.count()
    customers = q.order_by(Customer.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    # attach current unit allocation status
    result = []
    for c in customers:
        alloc = (
            db.query(UnitAllocation)
            .filter(
                UnitAllocation.ghng == c.ghng,
                UnitAllocation.status.in_([
                    AllocationStatus.PRE_ALLOCATED,
                    AllocationStatus.COMPETING,
                    AllocationStatus.HOLD,
                    AllocationStatus.ALLOCATED,
                ]),
            )
            .order_by(UnitAllocation.assigned_at.desc())
            .first()
        )
        result.append({
            "ghng": c.ghng,
            "name": c.name,
            "phone": c.phone,
            "unit_type_preference": c.unit_type_preference,
            "is_active": c.is_active,
            "registered_at": c.created_at,
            "allocation_status": alloc.status if alloc else None,
            "unit_id": alloc.unit_id if alloc else None,
        })

    return {"total": total, "page": page, "limit": limit, "customers": result}


@router.get("/{ghng}")
def get_customer(ghng: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.ghng == ghng).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    allocations = (
        db.query(UnitAllocation)
        .filter(UnitAllocation.ghng == ghng)
        .order_by(UnitAllocation.assigned_at.desc())
        .all()
    )
    return {
        "ghng": customer.ghng,
        "name": customer.name,
        "phone": customer.phone,
        "unit_type_preference": customer.unit_type_preference,
        "is_active": customer.is_active,
        "registered_at": customer.created_at,
        "allocations": [
            {
                "unit_id": a.unit_id,
                "status": a.status,
                "assigned_at": a.assigned_at,
                "paid_at": a.paid_at,
                "hold_expires_at": a.hold_expires_at,
            }
            for a in allocations
        ],
    }


@router.post("/", status_code=201)
def create_customer(body: CustomerCreate, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.ghng == body.ghng).first()
    if existing:
        raise HTTPException(status_code=409, detail="GHNG already registered")
    customer = Customer(**body.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return {"ghng": customer.ghng, "created": True}


@router.post("/bulk", status_code=201)
def bulk_create_customers(body: CustomerBulkCreate, db: Session = Depends(get_db)):
    created, skipped = 0, 0
    for c in body.customers:
        existing = db.query(Customer).filter(Customer.ghng == c.ghng).first()
        if existing:
            skipped += 1
            continue
        db.add(Customer(**c.model_dump()))
        created += 1
    db.commit()
    return {"created": created, "skipped": skipped, "total": len(body.customers)}


@router.patch("/{ghng}")
def update_customer(ghng: str, body: CustomerCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.ghng == ghng).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    return {"ghng": ghng, "updated": True}


@router.delete("/{ghng}")
def deactivate_customer(ghng: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.ghng == ghng).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer.is_active = 0
    db.commit()
    return {"ghng": ghng, "is_active": 0}
