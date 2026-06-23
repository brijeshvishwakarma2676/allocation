from pydantic import BaseModel


class PreAllocateRequest(BaseModel):
    mappings: list[dict]   # [{"ghng": "GHNG001", "unit_id": 123}, ...]


class PayRequest(BaseModel):
    ghng: str
    unit_id: int
    easebuzz_txn_id: str
