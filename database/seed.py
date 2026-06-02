"""Начальное заполнение базы данных продуктами из JSON-файла."""

import json
import logging
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.orm import Session

from database.engine import get_session
from database.models import FoodItem
from schemas.schemas import FoodItemCreate
from config import SEED_FILE

logger = logging.getLogger(__name__)

DATA_FILE = SEED_FILE
BATCH_SIZE = 500


def _load_raw_data() -> list[dict]:
    """Загружает сырые данные из JSON-файла."""
    if not DATA_FILE.exists():
        logger.warning(f"Seed файл не найден: {DATA_FILE}")
        return []

    with DATA_FILE.open(encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return []

    if not isinstance(data, list):
        logger.error("В JSON файле должен быть список")
        return []

    return data


def _validate_records(raw_list: list[dict]) -> list[FoodItemCreate]:
    """Валидирует записи с помощью Pydantic схемы."""
    valid: list[FoodItemCreate] = []
    for i, raw in enumerate(raw_list):
        try:
            valid.append(FoodItemCreate.model_validate(raw))
        except ValidationError as e:
            logger.warning(f"Пропускается #{i} ({raw.get('name', '?')}): {e}")
    logger.info(f"Проверено {len(valid)}/{len(raw_list)} записей")
    return valid


def _get_existing_names(session: Session) -> set[str]:
    """
    Возвращает множество названий уже существующих продуктов 
    (только не кастомных).
    """
    rows = session.query(FoodItem.name_lower).filter(
        FoodItem.is_custom == False).all()
    return {row[0] for row in rows}


def _build_food_item(data: FoodItemCreate) -> FoodItem:
    """Создаёт объект FoodItem из валидированных данных."""
    return FoodItem(
        name=data.name,
        name_lower=data.name.lower(),
        calories=data.calories,
        protein=data.protein,
        fat=data.fat,
        carbs=data.carbs,
        is_custom=False,
        source="parsed",
    )


def seed_initial_foods() -> None:
    """
    Заполняет таблицу food_items начальными данными,
    если они ещё не были загружены.
    Проверяет наличие записей с source='parsed' — если есть, пропускает.
    """
    session = get_session()
    try:
        existing_parsed = session.query(FoodItem).filter(
            FoodItem.source == "parsed").first()
        if existing_parsed:
            logger.info(
                "Seed уже выполнен (есть записи с source='parsed'), пропускаем.")
            return
    finally:
        session.close()

    raw_list = _load_raw_data()
    if not raw_list:
        return

    validated = _validate_records(raw_list)
    if not validated:
        logger.error("Нет валидных записей для загрузки")
        return

    session = get_session()
    try:
        existing_names = _get_existing_names(session)
        logger.info(f"Уже в БД (parsed): {len(existing_names)} записей")

        to_insert = [item for item in validated if item.name.lower()
                     not in existing_names]

        if not to_insert:
            logger.info("Нет новых продуктов для вставки, пропускаем.")
            return

        logger.info(f"Вставляем {len(to_insert)} новых продуктов...")
        inserted_total = 0
        for batch_start in range(0, len(to_insert), BATCH_SIZE):
            batch = to_insert[batch_start: batch_start + BATCH_SIZE]
            food_items = [_build_food_item(item) for item in batch]
            session.bulk_save_objects(food_items)
            session.commit()
            inserted_total += len(food_items)
            logger.info(f"  ...вставлено {inserted_total}/{len(to_insert)}")

        logger.info(f"Seed завершён: добавлено {inserted_total} продуктов.")
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка seed: {e}", exc_info=True)
        raise
    finally:
        session.close()
