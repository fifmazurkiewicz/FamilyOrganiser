import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.models.transfer import TransferType
from app.services.transfer import TransferService

router = APIRouter(prefix="/transfers", tags=["Transfers"])


class TransferCreate(BaseModel):
    transfer_type: TransferType
    from_account_id: Optional[uuid.UUID] = None
    to_account_id: Optional[uuid.UUID] = None
    from_goal_id: Optional[uuid.UUID] = None
    to_goal_id: Optional[uuid.UUID] = None
    amount: float
    currency: str = "PLN"
    transfer_date: date
    description: Optional[str] = None


class TransferResponse(BaseModel):
    id: uuid.UUID
    transfer_type: TransferType
    from_account_id: Optional[uuid.UUID] = None
    to_account_id: Optional[uuid.UUID] = None
    from_goal_id: Optional[uuid.UUID] = None
    to_goal_id: Optional[uuid.UUID] = None
    amount: float
    currency: str
    transfer_date: date
    description: Optional[str] = None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[TransferResponse])
async def list_transfers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    transfers = await TransferService(db).list(current_user.id)
    return transfers


@router.post("/", response_model=TransferResponse, status_code=201)
async def create_transfer(
    data: TransferCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TransferService(db).create(current_user.id, data.model_dump())
