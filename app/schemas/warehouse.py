from pydantic import BaseModel
from typing import Optional


class WarehouseBase(BaseModel):
    name: str
    branch_id: int


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    branch_id: Optional[int] = None


class WarehouseResponse(WarehouseBase):
    id: int

    class Config:
        from_attributes = True


# Alias for compatibility
Warehouse = WarehouseResponse 