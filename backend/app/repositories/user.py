from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, SecurityQuestion
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_security_question(self, user_id) -> SecurityQuestion | None:
        result = await self._session.execute(
            select(SecurityQuestion).where(SecurityQuestion.user_id == user_id)
        )
        return result.scalar_one_or_none()
