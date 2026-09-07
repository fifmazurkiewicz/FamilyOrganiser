"""Seed default admin user."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password, hash_security_answer
from app.models.user import User, SecurityQuestion


async def seed_admin_user(db: AsyncSession) -> None:
    """Create or sync default admin from ADMIN_EMAIL / ADMIN_PASSWORD.

    When Supabase Auth is enabled, only promote existing user by email —
    do not invent local passwords.
    """
    if settings.supabase_auth_enabled:
        result = await db.execute(
            select(User).where(User.email == settings.ADMIN_EMAIL.lower()).limit(1)
        )
        admin = result.scalar_one_or_none()
        if admin is not None:
            admin.is_app_admin = True
            admin.is_locked = False
            admin.is_active = True
            await db.commit()
        return

    result = await db.execute(select(User).where(User.email == settings.ADMIN_EMAIL).limit(1))
    admin = result.scalar_one_or_none()
    password_hash = hash_password(settings.ADMIN_PASSWORD)

    if admin is None:
        admin = User(
            email=settings.ADMIN_EMAIL,
            hashed_password=password_hash,
            full_name="Administrator",
            default_currency="PLN",
            is_app_admin=True,
            is_active=True,
            is_locked=False,
            is_approved=True,
        )
        db.add(admin)
        await db.flush()

        db.add(
            SecurityQuestion(
                user_id=admin.id,
                question="Jak miało na imię Twoje pierwsze zwierzę domowe?",
                hashed_answer=hash_security_answer(settings.ADMIN_PASSWORD),
            )
        )
        await db.commit()
        return

    # Always sync seed admin credentials from .env (local/dev bootstrap)
    admin.hashed_password = password_hash
    admin.is_app_admin = True
    admin.is_locked = False
    admin.is_active = True
    await db.commit()
