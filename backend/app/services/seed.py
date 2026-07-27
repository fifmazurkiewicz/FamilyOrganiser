"""Seed default admin user."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password, hash_security_answer
from app.models.user import User, SecurityQuestion


async def seed_admin_user(db: AsyncSession) -> None:
    """Create default admin account from ADMIN_EMAIL / ADMIN_PASSWORD if not exists."""
    result = await db.execute(select(User).where(User.email == settings.ADMIN_EMAIL).limit(1))
    if result.scalar_one_or_none():
        return

    admin = User(
        email=settings.ADMIN_EMAIL,
        hashed_password=hash_password(settings.ADMIN_PASSWORD),
        full_name="Administrator",
        default_currency="PLN",
        is_app_admin=True,
    )
    db.add(admin)
    await db.flush()

    sq = SecurityQuestion(
        user_id=admin.id,
        question="Jak miało na imię Twoje pierwsze zwierzę domowe?",
        hashed_answer=hash_security_answer(settings.ADMIN_PASSWORD),
    )
    db.add(sq)
    await db.commit()
