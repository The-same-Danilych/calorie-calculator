# services/user_service.py
from typing import Callable, Optional
from database.models import User
from database.engine import get_session
from schemas.schemas import UserCreate
from utils.mifflin import calculate_goals
from utils.async_db import run_in_background


def create_or_update_user_async(data: UserCreate, on_done: Callable[[User], None], on_error: Callable[[Exception], None]) -> None:
    """Асинхронно создаёт/обновляет пользователя и вызывает callback в главном потоке."""
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
    """Асинхронно получает пользователя."""
    def _sync_task() -> Optional[User]:
        session = get_session()
        try:
            return session.query(User).first()
        finally:
            session.close()

    run_in_background(_sync_task, on_result)
