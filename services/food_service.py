"""
Сервис для работы с продуктами: поиск, добавление
"""

from database.models import FoodItem
from database.engine import get_session
from schemas.schemas import FoodItemCreate
from typing import Optional


def search_food(query: str, limit: int = 10) -> list[FoodItem]:
    """
    Поиск продуктов по названию
    (регистронезависимый, частичное совпадение).
    """
    session = get_session()
    try:
        q = query.strip().lower()
        return (session.query(FoodItem)
                .filter(FoodItem.name_lower.contains(q))
                .order_by(FoodItem.is_custom.desc())
                .limit(limit)
                .all())
    finally:
        session.close()


def add_food(data: FoodItemCreate) -> FoodItem:
    """
    Добавляет новый продукт в базу
    (обычно кастомный, созданный пользователем).
    """
    session = get_session()
    try:
        item = FoodItem(
            name=data.name.strip(),
            name_lower=data.name.strip().lower(),
            calories=data.calories,
            protein=data.protein,
            fat=data.fat,
            carbs=data.carbs,
            is_custom=data.is_custom,
            source="user" if data.is_custom else "parsed",
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_food_item(food_id: int) -> Optional[FoodItem]:
    """Возвращает продукт по ID."""
    session = get_session()
    try:
        return session.query(FoodItem).filter_by(id=food_id).first()
    finally:
        session.close()
