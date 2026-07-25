from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class ShoppingItemCreate(BaseModel):
    name: str
    quantity: int = 1


class ShoppingItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    is_bought: Optional[bool] = None


class ShoppingItemResponse(BaseModel):
    id: uuid.UUID
    list_id: uuid.UUID
    name: str
    quantity: int
    added_by: uuid.UUID
    bought_by: Optional[uuid.UUID] = None
    bought_at: Optional[datetime] = None
    is_bought: bool

    model_config = {"from_attributes": True}


class ShoppingListCreate(BaseModel):
    name: str
    family_group_id: uuid.UUID


class ShoppingListUpdate(BaseModel):
    name: Optional[str] = None


class ShoppingListResponse(BaseModel):
    id: uuid.UUID
    family_group_id: uuid.UUID
    name: str
    created_by: uuid.UUID
    created_at: datetime
    items: list[ShoppingItemResponse] = []

    model_config = {"from_attributes": True}