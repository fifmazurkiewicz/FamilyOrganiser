import uuid
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.user import User
from app.models.savings import SavingsGoal, SavingsContribution
from app.schemas.savings import (
    SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalResponse,
    ContributionCreate, ContributionResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/savings", tags=["savings"])


def _compute_progress(goal: SavingsGoal) -> float:
    if goal.target_amount == 0:
        return 0.0
    return float(goal.current_amount / goal.target_amount * 100)


def _to_response(goal: SavingsGoal) -> SavingsGoalResponse:
    return SavingsGoalResponse(
        id=goal.id,
        user_id=goal.user_id,
        name=goal.name,
        description=goal.description,
        icon=goal.icon,
        color=goal.color,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        currency=goal.currency,
        goal_type=goal.goal_type,
        visibility=goal.visibility,
        target_date=goal.target_date,
        monthly_contribution=goal.monthly_contribution,
        is_completed=goal.is_completed,
        is_active=goal.is_active,
        priority=goal.priority,
        progress_percent=_compute_progress(goal),
        created_at=goal.created_at,
    )


@router.post("/goals", response_model=SavingsGoalResponse, status_code=201)
async def create_goal(
    payload: SavingsGoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal = SavingsGoal(
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        icon=payload.icon,
        color=payload.color,
        target_amount=payload.target_amount,
        currency=payload.currency,
        goal_type=payload.goal_type,
        visibility=payload.visibility,
        target_date=payload.target_date,
        monthly_contribution=payload.monthly_contribution,
        linked_account_id=payload.linked_account_id,
        family_group_id=payload.family_group_id,
        priority=payload.priority,
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return _to_response(goal)


@router.get("/goals", response_model=list[SavingsGoalResponse])
async def list_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SavingsGoal).where(
            SavingsGoal.user_id == current_user.id,
            SavingsGoal.is_active == True,
        ).order_by(SavingsGoal.priority.desc())
    )
    return [_to_response(g) for g in result.scalars().all()]


@router.get("/goals/{goal_id}", response_model=SavingsGoalResponse)
async def get_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SavingsGoal).where(
            SavingsGoal.id == goal_id, SavingsGoal.user_id == current_user.id
        )
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return _to_response(goal)


@router.patch("/goals/{goal_id}", response_model=SavingsGoalResponse)
async def update_goal(
    goal_id: uuid.UUID,
    payload: SavingsGoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SavingsGoal).where(
            SavingsGoal.id == goal_id, SavingsGoal.user_id == current_user.id
        )
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(goal, field, value)
    await db.commit()
    await db.refresh(goal)
    return _to_response(goal)


@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SavingsGoal).where(
            SavingsGoal.id == goal_id, SavingsGoal.user_id == current_user.id
        )
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal.is_active = False
    await db.commit()
    return {"message": "Goal deactivated"}


@router.post("/goals/{goal_id}/contributions", response_model=ContributionResponse, status_code=201)
async def add_contribution(
    goal_id: uuid.UUID,
    payload: ContributionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SavingsGoal).where(SavingsGoal.id == goal_id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    contribution = SavingsContribution(
        goal_id=goal_id,
        user_id=current_user.id,
        source_account_id=payload.source_account_id,
        amount=payload.amount,
        currency=goal.currency,
        contribution_date=payload.contribution_date,
        note=payload.note,
        is_withdrawal=payload.is_withdrawal,
    )
    db.add(contribution)

    # Update goal balance
    if payload.is_withdrawal:
        goal.current_amount -= payload.amount
    else:
        goal.current_amount += payload.amount
        if goal.current_amount >= goal.target_amount:
            goal.is_completed = True

    await db.commit()
    await db.refresh(contribution)
    return contribution


@router.get("/goals/{goal_id}/contributions", response_model=list[ContributionResponse])
async def list_contributions(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SavingsContribution).where(SavingsContribution.goal_id == goal_id)
        .order_by(SavingsContribution.contribution_date.desc())
    )
    return result.scalars().all()
