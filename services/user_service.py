"""
Сервис для работы с пользователем:
создание, обновление, удаление, получение.
"""

from typing import Callable, Optional
from database.models import User
from database.engine import get_session
from schemas.schemas import UserCreate
from utils.mifflin import calculate_goals
from utils.async_db import run_in_background


def create_or_update_user_async(data: UserCreate,
                                on_done: Callable[[User], None],
                                on_error: Callable[[Exception], None]) -> None:
    """
    Асинхронно создаёт или обновляет пользователя
    (в БД может быть только один).
    """
    def _sync_task() -> User:
        session = get_session()
        goals = calculate_goals(data.gender, data.weight_kg, data.height_cm,
                                data.years, data.activity, data.goal)
        try:
            user = session.query(User).first()
            if user:
                for field, value in data.model_dump().items():
                    setattr(user, field, value)
            else:
                user = User(**data.model_dump())
                session.add(user)

            for field, value in goals.items():
                setattr(user, field, value)

            session.commit()
            session.refresh(user)
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    run_in_background(_sync_task, on_done, on_error)


def get_user_async(on_result: Callable[[Optional[User]], None]) -> None:
    """Асинхронно получает пользователя (первого из БД)."""
    def _sync_task() -> Optional[User]:
        session = get_session()
        try:
            return session.query(User).first()
        finally:
            session.close()

    run_in_background(_sync_task, on_result)


def delete_user_async(user_id: int) -> None:
    """Удаляет пользователя и все связанные записи (каскадно)."""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            session.delete(user)
            session.commit()
    finally:
        session.close()


def update_user_goals_sync(user_id: int, new_weight_kg: float, goal: str, activity: str):
    """
    Обновляет вес, цель и уровень активности, пересчитывает целевые КБЖУ.
    Выполняется синхронно (для фонового вызова).
    """
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise ValueError("User not found")
        user.weight_kg = new_weight_kg
        user.goal = goal
        user.activity = activity
        new_goals = calculate_goals(
            gender=user.gender,
            weight_kg=user.weight_kg,
            height_cm=user.height_cm,
            age=user.years,
            activity=activity,
            goal=goal
        )
        user.calorie_goal = new_goals["calorie_goal"]
        user.protein_goal = new_goals["protein_goal"]
        user.fat_goal = new_goals["fat_goal"]
        user.carb_goal = new_goals["carb_goal"]
        session.commit()
        return user
    finally:
        session.close()
