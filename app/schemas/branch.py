from pydantic import BaseModel
from typing import Optional


class BranchBase(BaseModel):
    name: str
    location: str


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BranchBase):
    name: Optional[str] = None
    location: Optional[str] = None


class BranchResponse(BranchBase):
    id: int

    class Config:
        from_attributes = True 