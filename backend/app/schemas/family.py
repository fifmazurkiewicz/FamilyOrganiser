from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
from app.models.family import FamilyRole


class FamilyGroupCreate(BaseModel):
    name: str


class FamilyGroupUpdate(BaseModel):
    name: Optional[str] = None


class FamilyGroupResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    member_count: int = 0
    pending_requests: int = 0

    model_config = {"from_attributes": True}


class MembershipResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    family_group_id: uuid.UUID
    role: FamilyRole
    joined_at: datetime
    share_expenses: bool
    share_investments: bool
    share_savings: bool
    share_budget: bool

    model_config = {"from_attributes": True}


class MemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    email: str
    avatar_url: Optional[str] = None
    role: FamilyRole
    joined_at: datetime

    model_config = {"from_attributes": True}


class SharingPreferencesUpdate(BaseModel):
    share_expenses: Optional[bool] = None
    share_investments: Optional[bool] = None
    share_savings: Optional[bool] = None
    share_budget: Optional[bool] = None


class InvitationLinkCreate(BaseModel):
    single_use: bool = True
    expire_days: int = 7


class InvitationLinkResponse(BaseModel):
    id: uuid.UUID
    token: str
    single_use: bool
    used: bool
    expires_at: datetime
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TransferAdminRoleRequest(BaseModel):
    new_admin_user_id: uuid.UUID
