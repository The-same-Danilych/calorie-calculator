from sqlalchemy import func, cast, Date
from database.models import DiaryEntry, FoodItem
from database.engine import get_session
from schemas.schemas import DiaryEntryCreate, DiaryEntryUpdate
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from typing import Optional
from services.food_service import add_food


def add_diary_entry(user_id: int, data: DiaryEntryCreate) -> DiaryEntry:
    session = get_session()
    try:
        food = session.query(FoodItem).filter_by(id=data.food_item_id).first()
        if food is None:
            raise ValueError(f"FoodItem id={data.food_item_id} not found")
        factor = data.grams / 100

        entry = DiaryEntry(
            user_id=user_id,
            food_item_id=data.food_item_id,
            grams=data.grams,
            meal_type=data.meal_type,
            calories=round(food.calories * factor, 1),
            protein=round(food.protein * factor, 1),
            fat=round(food.fat * factor, 1),
            carbs=round(food.carbs * factor, 1),
        )
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_day_summary(user_id: int, day: date = None) -> dict:
    session = get_session()
    day = day or date.today()
    try:
        entries = (session.query(DiaryEntry)
                   .options(joinedload(DiaryEntry.food_item))
                   .filter(DiaryEntry.user_id == user_id)
                   .filter(func.date(DiaryEntry.eaten_at) == day)
                   .all())

        meals = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
        totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}

        for e in entries:
            meals[e.meal_type].append(e)
            totals["calories"] += e.calories
            totals["protein"] += e.protein
            totals["fat"] += e.fat
            totals["carbs"] += e.carbs

        return {"meals": meals, "totals": totals, "date": day}
    finally:
        session.close()


def get_week_calories(user_id: int) -> list[dict]:
    session = get_session()
    try:
        rows = (session.query(
            func.date(DiaryEntry.eaten_at).label("day"),
            func.sum(DiaryEntry.calories).label("total"))
            .filter(DiaryEntry.user_id == user_id)
            .group_by(func.date(DiaryEntry.eaten_at))
            .order_by(func.date(DiaryEntry.eaten_at).desc())
            .limit(7)
            .all())
        return [{"date": r.day, "calories": round(r.total, 1)} for r in rows]
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete_entry(entry_id: int) -> bool:
    """Удаление записи из дневника."""
    session = get_session()
    try:
        entry = session.query(DiaryEntry).filter_by(id=entry_id).first()
        if entry:
            session.delete(entry)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_diary_entry(entry_id: int) -> Optional[DiaryEntry]:
    """Возвращает запись дневника по ID вместе с привязанным продуктом."""
    session = get_session()
    try:
        return (session.query(DiaryEntry)
                .options(joinedload(DiaryEntry.food_item))
                .filter(DiaryEntry.id == entry_id)
                .first())
    finally:
        session.close()


def update_diary_entry(entry_id: int,
                       update_data: DiaryEntryUpdate) -> DiaryEntry:
    """
    Обновляет существующую запись дневника.
    Можно изменить граммы, приём пищи и/или данные продукта.
    Если переданы food_data, создаётся новый кастомный продукт,
    и запись привязывается к нему.
    """
    session = get_session()
    try:
        entry = session.query(DiaryEntry).filter_by(id=entry_id).first()
        if not entry:
            raise ValueError(f"DiaryEntry id={entry_id} не найден")

        if update_data.food_data:
            new_food = add_food(update_data.food_data)
            entry.food_item_id = new_food.id
            entry.food_item = new_food
        else:
            if entry.food_item is None:
                session.refresh(entry, attribute_names=['food_item'])
            new_food = entry.food_item

        if update_data.grams is not None:
            entry.grams = update_data.grams
        if update_data.meal_type is not None:
            entry.meal_type = update_data.meal_type

        factor = entry.grams / 100.0
        entry.calories = round(new_food.calories * factor, 1)
        entry.protein = round(new_food.protein * factor, 1)
        entry.fat = round(new_food.fat * factor, 1)
        entry.carbs = round(new_food.carbs * factor, 1)

        session.commit()
        session.refresh(entry)
        return entry
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
