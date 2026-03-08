"""Seed default transaction categories and admin user."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password, hash_security_answer
from app.models.transaction import TransactionCategory
from app.models.user import User, SecurityQuestion

DEFAULT_CATEGORIES = [
    {"name": "Jedzenie", "icon": "🍽️", "color": "#FF6B6B", "children": [
        {"name": "Sklep spożywczy", "icon": "🛒"},
        {"name": "Restauracja", "icon": "🍴"},
        {"name": "Kawiarnia", "icon": "☕"},
        {"name": "Dostawa jedzenia", "icon": "🛵"},
    ]},
    {"name": "Transport", "icon": "🚗", "color": "#4ECDC4", "children": [
        {"name": "Paliwo", "icon": "⛽"},
        {"name": "Komunikacja miejska", "icon": "🚌"},
        {"name": "Taxi / Uber", "icon": "🚕"},
        {"name": "Parking", "icon": "🅿️"},
    ]},
    {"name": "Zdrowie", "icon": "❤️", "color": "#FF6B6B", "children": [
        {"name": "Leki", "icon": "💊"},
        {"name": "Lekarz", "icon": "🏥"},
        {"name": "Siłownia", "icon": "💪"},
    ]},
    {"name": "Edukacja", "icon": "📚", "color": "#45B7D1", "children": [
        {"name": "Kursy", "icon": "🎓"},
        {"name": "Książki", "icon": "📖"},
    ]},
    {"name": "Rozrywka", "icon": "🎬", "color": "#96CEB4", "children": [
        {"name": "Kino / Theater", "icon": "🎭"},
        {"name": "Streaming", "icon": "📺"},
        {"name": "Gry", "icon": "🎮"},
    ]},
    {"name": "Mieszkanie", "icon": "🏠", "color": "#FFEAA7", "children": [
        {"name": "Czynsz", "icon": "🔑"},
        {"name": "Media", "icon": "💡"},
        {"name": "Internet", "icon": "📡"},
        {"name": "Remont", "icon": "🔨"},
    ]},
    {"name": "Ubrania", "icon": "👗", "color": "#DDA0DD", "children": []},
    {"name": "Inne", "icon": "📦", "color": "#B0C4DE", "children": []},
    # Kategorie przychodów
    {"name": "Przychody", "icon": "💰", "color": "#10b981", "children": [
        {"name": "Praca", "icon": "💼"},
        {"name": "Freelance", "icon": "💻"},
        {"name": "Premia", "icon": "🎁"},
        {"name": "Dywidenda", "icon": "📈"},
        {"name": "Wynajem", "icon": "🏠"},
        {"name": "Sprzedaż", "icon": "🛒"},
        {"name": "Darowizna", "icon": "🎗️"},
        {"name": "Inne przychody", "icon": "📥"},
    ]},
]


INCOME_CATEGORIES = [
    {"name": "Przychody", "icon": "💰", "color": "#10b981", "children": [
        {"name": "Praca", "icon": "💼"},
        {"name": "Freelance", "icon": "💻"},
        {"name": "Premia", "icon": "🎁"},
        {"name": "Dywidenda", "icon": "📈"},
        {"name": "Wynajem", "icon": "🏠"},
        {"name": "Sprzedaż", "icon": "🛒"},
        {"name": "Darowizna", "icon": "🎗️"},
        {"name": "Inne przychody", "icon": "📥"},
    ]},
]


async def seed_categories(db: AsyncSession):
    result = await db.execute(
        select(TransactionCategory).where(TransactionCategory.is_system == True).limit(1)
    )
    already_seeded = result.scalar_one_or_none() is not None

    if not already_seeded:
        for cat_data in DEFAULT_CATEGORIES:
            parent = TransactionCategory(
                name=cat_data["name"],
                icon=cat_data.get("icon"),
                color=cat_data.get("color"),
                is_system=True,
            )
            db.add(parent)
            await db.flush()

            for child_data in cat_data.get("children", []):
                child = TransactionCategory(
                    name=child_data["name"],
                    icon=child_data.get("icon"),
                    parent_id=parent.id,
                    is_system=True,
                )
                db.add(child)
    else:
        # Dodaj kategorie przychodów, jeśli jeszcze nie istnieją (np. po aktualizacji)
        existing = await db.execute(
            select(TransactionCategory).where(
                TransactionCategory.name == "Przychody",
                TransactionCategory.is_system == True,
            )
        )
        if existing.scalar_one_or_none() is None:
            for cat_data in INCOME_CATEGORIES:
                parent = TransactionCategory(
                    name=cat_data["name"],
                    icon=cat_data.get("icon"),
                    color=cat_data.get("color"),
                    is_system=True,
                )
                db.add(parent)
                await db.flush()

                for child_data in cat_data.get("children", []):
                    child = TransactionCategory(
                        name=child_data["name"],
                        icon=child_data.get("icon"),
                        parent_id=parent.id,
                        is_system=True,
                    )
                    db.add(child)

    await db.commit()


async def seed_admin_user(db: AsyncSession) -> None:
    """Create default admin account from ADMIN_EMAIL / ADMIN_PASSWORD if not exists."""
    result = await db.execute(select(User).where(User.email == settings.ADMIN_EMAIL).limit(1))
    if result.scalar_one_or_none():
        return  # Already exists

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
