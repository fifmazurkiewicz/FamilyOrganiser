import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.services.savings import SavingsService
from app.schemas.savings import (
    SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalResponse,
    ContributionCreate, ContributionResponse,
)

router = APIRouter(prefix="/savings", tags=["Savings"])


@router.get("/", response_model=list[SavingsGoalResponse])
async def list_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SavingsService(db).list_goals(current_user.id)


@router.post("/", response_model=SavingsGoalResponse, status_code=201)
async def create_goal(
    data: SavingsGoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SavingsService(db).create_goal(current_user.id, data)


@router.get("/{goal_id}", response_model=SavingsGoalResponse)
async def get_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SavingsService(db).get_goal(current_user.id, goal_id)


@router.patch("/{goal_id}", response_model=SavingsGoalResponse)
async def update_goal(
    goal_id: uuid.UUID,
    data: SavingsGoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SavingsService(db).update_goal(current_user.id, goal_id, data)


@router.delete("/{goal_id}", status_code=204)
async def delete_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await SavingsService(db).delete_goal(current_user.id, goal_id)


@router.get("/{goal_id}/contributions", response_model=list[ContributionResponse])
async def list_contributions(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SavingsService(db).list_contributions(current_user.id, goal_id)


@router.post("/{goal_id}/contributions", response_model=ContributionResponse, status_code=201)
async def add_contribution(
    goal_id: uuid.UUID,
    data: ContributionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SavingsService(db).add_contribution(current_user.id, goal_id, data)
