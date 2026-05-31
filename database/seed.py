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
    if not DATA_FILE.exists():
        logger.warning(f"Seed файл не найден: {DATA_FILE}")
        return []

    with DATA_FILE.open(encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсирования из JSON файла: {e}")
            return []

    if not isinstance(data, list):
        logger.error("В JSON файле должен быть список")
        return []

    return data


def _validate_records(raw_list: list[dict]) -> list[FoodItemCreate]:
    valid: list[FoodItemCreate] = []

    for i, raw in enumerate(raw_list):
        try:
            valid.append(FoodItemCreate.model_validate(raw))
        except ValidationError as e:
            logger.warning(
                f"Пропускается #{i} ({raw.get('name', '?')}): {e}")

    logger.info(f"Проверенно {len(valid)}/{len(raw_list)} записей")
    return valid


def _get_existing_names(session: Session) -> set[str]:
    rows = (
        session.query(FoodItem.name_lower)
        .filter(FoodItem.is_custom == False)  # noqa: E712
        .all()
    )
    return {row[0] for row in rows}


def _build_food_item(data: FoodItemCreate) -> FoodItem:
    return FoodItem(
        name=data.name,
        name_lower=data.name.lower(),
        calories=data.calories,
        protein=data.protein,
        fat=data.fat,
        carbs=data.carbs,
        barcode=data.barcode,
        is_custom=False,
        source="parsed",
    )


def seed_initial_foods() -> None:
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
        logger.error("No valid records to seed")
        return

    session = get_session()
    try:
        existing_names = _get_existing_names(session)
        logger.info(f"Already in DB (parsed): {len(existing_names)} items")

        to_insert = [
            item for item in validated
            if item.name.lower() not in existing_names
        ]

        if not to_insert:
            logger.info("Seed: nothing new to insert, skipping")
            return

        logger.info(f"Inserting {len(to_insert)} new food items...")

        inserted_total = 0
        for batch_start in range(0, len(to_insert), BATCH_SIZE):
            batch = to_insert[batch_start: batch_start + BATCH_SIZE]
            food_items = [_build_food_item(item) for item in batch]
            session.bulk_save_objects(food_items)
            session.commit()
            inserted_total += len(food_items)
            logger.info(f"  ...inserted {inserted_total}/{len(to_insert)}")

        logger.info(f"Seed complete: {inserted_total} items added")

    except Exception as e:
        session.rollback()
        logger.error(f"Seed failed: {e}", exc_info=True)
        raise
    finally:
        session.close()
