"""Настройка SQLAlchemy: движок, сессии, инициализация БД."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base
from config import DB_URL
import os

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def init_db() -> None:
    """Создаёт все таблицы, если они ещё не существуют."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Возвращает новую сессию для работы с БД."""
    return SessionLocal()


def delete_database() -> bool:
    """
    Полностью удаляет файл базы данных SQLite.
    Возвращает True, если файл удалён, иначе False.
    """
    engine.dispose()

    if DB_URL.startswith("sqlite:///"):
        db_path = DB_URL.replace("sqlite:///", "")
    else:
        db_path = DB_URL

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"База данных удалена: {db_path}")
            return True
        except Exception as e:
            print(f"Ошибка удаления БД: {e}")
            return False
    else:
        print(f"Файл БД не найден: {db_path}")
        return False
