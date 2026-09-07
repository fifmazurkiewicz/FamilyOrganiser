"""Resolve / provision app User from Supabase Auth JWT claims."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User

BOOTSTRAP_ADMIN_EMAIL = "fifmazurkiewicz@gmail.com"


def is_admin_allowlist(email: str) -> bool:
    normalized = (email or "").strip().lower()
    if not normalized:
        return False
    return normalized in {
        BOOTSTRAP_ADMIN_EMAIL,
        settings.ADMIN_EMAIL.strip().lower(),
    }


def apply_admin_allowlist(user: User, email: str) -> bool:
    """Promote allowlist emails to approved app-admin on every login."""
    if not is_admin_allowlist(email):
        return False
    changed = False
    if not user.is_app_admin:
        user.is_app_admin = True
        changed = True
    if not user.is_approved:
        user.is_approved = True
        changed = True
    return changed


async def get_or_create_user_from_claims(
    db: AsyncSession, claims: dict
) -> User | None:
    sub_raw = claims.get("sub")
    if not sub_raw:
        return None

    try:
        auth_id = uuid.UUID(str(sub_raw))
    except ValueError:
        return None

    meta = claims.get("user_metadata") or {}
    if not isinstance(meta, dict):
        meta = {}

    email = (
        (claims.get("email") or meta.get("email") or "").strip().lower()
    )
    full_name = (
        (meta.get("full_name") or meta.get("name") or claims.get("name") or "")
        .strip()
        or (email.split("@")[0] if email else "Użytkownik")
    )[:100]

    result = await db.execute(select(User).where(User.supabase_auth_id == auth_id))
    user = result.scalar_one_or_none()
    if user:
        changed = False
        if email and user.email != email:
            user.email = email
            changed = True
        if full_name and user.full_name != full_name and user.full_name in ("", "Użytkownik"):
            user.full_name = full_name
            changed = True
        if apply_admin_allowlist(user, email):
            changed = True
        if changed:
            await db.commit()
            await db.refresh(user)
        return user

    if email:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            user.supabase_auth_id = auth_id
            if not user.full_name and full_name:
                user.full_name = full_name
            apply_admin_allowlist(user, email)
            await db.commit()
            await db.refresh(user)
            return user

    if not email:
        return None

    allowlist = is_admin_allowlist(email)
    user = User(
        email=email,
        hashed_password=None,
        full_name=full_name,
        supabase_auth_id=auth_id,
        default_currency="PLN",
        is_app_admin=allowlist,
        is_approved=allowlist,
        is_active=True,
        is_locked=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
