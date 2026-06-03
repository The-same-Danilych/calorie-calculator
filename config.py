"""
Модуль конфигурации приложения (config.py).
Предоставляет централизованное управление настройками, путями к файлам
и ресурсам с учетом кроссплатформенности (Android / Desktop).
"""
from pathlib import Path
import sys

BASE_DIR = Path(__file__).parent.resolve()


def _is_android() -> bool:
    return "android" in sys.modules


IS_ANDROID = _is_android()
IS_MOBILE = IS_ANDROID


DEBUG = not IS_MOBILE


def _get_storage_dir() -> Path:
    """Return platform-specific writable storage directory."""
    if IS_ANDROID:
        from android.storage import app_storage_path
        return Path(app_storage_path())
    else:
        storage = BASE_DIR / "data"
        storage.mkdir(exist_ok=True)
        return storage


STORAGE_DIR = _get_storage_dir()
DB_PATH = STORAGE_DIR / "calories.db"
DB_URL = f"sqlite:///{DB_PATH}"
LOG_FILE = STORAGE_DIR / "app.log"

ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"

SEED_FILE = BASE_DIR / "database" / "seed_data" / "initial_food.json"


def image(filename: str) -> str:
    """Возвращает абсолютный путь к изображению в папке assets/images."""
    return str(IMAGES_DIR / filename)
