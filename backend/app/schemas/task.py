from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
import uuid


class TaskItemCreate(BaseModel):
    title: str
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[date] = None


class TaskItemUpdate(BaseModel):
    title: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    is_done: Optional[bool] = None
    due_date: Optional[date] = None


class TaskItemResponse(BaseModel):
    id: uuid.UUID
    list_id: uuid.UUID
    title: str
    assigned_to: Optional[uuid.UUID] = None
    done_by: Optional[uuid.UUID] = None
    done_at: Optional[datetime] = None
    is_done: bool
    due_date: Optional[date] = None

    model_config = {"from_attributes": True}


class TaskListCreate(BaseModel):
    name: str
    family_group_id: uuid.UUID


class TaskListUpdate(BaseModel):
    name: Optional[str] = None


class TaskListResponse(BaseModel):
    id: uuid.UUID
    family_group_id: uuid.UUID
    name: str
    created_by: uuid.UUID
    created_at: datetime
    items: list[TaskItemResponse] = []

    model_config = {"from_attributes": True}