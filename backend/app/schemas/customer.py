from typing import Optional
from pydantic import BaseModel


class CustomerCreate(BaseModel):
    ghng: str
    name: Optional[str] = None
    phone: Optional[str] = None
    unit_type_preference: Optional[str] = None


class CustomerBulkCreate(BaseModel):
    customers: list[CustomerCreate]
