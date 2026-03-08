"""Seed default transaction categories."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.transaction import TransactionCategory

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
]


async def seed_categories(db: AsyncSession):
    result = await db.execute(
        select(TransactionCategory).where(TransactionCategory.is_system == True).limit(1)
    )
    if result.scalar_one_or_none():
        return  # Already seeded

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

    await db.commit()
