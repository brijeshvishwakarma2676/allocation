from pydantic import BaseModel


class EnablePreferenceRequest(BaseModel):
    project_id: str    # Mavis project string ID, e.g. "project-1728380099837"
    preference: int    # 2 or 3


class AssignUnitRequest(BaseModel):
    ghng: str
    unit_id: int
