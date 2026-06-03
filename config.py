"""
Модуль конфигурации приложения (config.py).
Предоставляет централизованное управление настройками, путями к файлам
и ресурсам с учетом кроссплатформенности (Android / Desktop).
"""
from pathlib import Path
import sys
import shutil

BASE_DIR = Path(__file__).parent.resolve()


def _is_android() -> bool:
    return "android" in sys.modules


IS_ANDROID = _is_android()
IS_MOBILE = IS_ANDROID

DEBUG = not IS_MOBILE


def _get_storage_dir() -> Path:
    """
    Возвращает каталог хранилища, доступный для записи,
    специфичный для данной платформы.
    """
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

STORAGE_IMAGES_DIR = STORAGE_DIR / "images"

SEED_FILE = BASE_DIR / "database" / "seed_data" / "initial_food.json"


def _copy_assets_to_storage():
    """
    Копирует изображения из assets/images в STORAGE_IMAGES_DIR.
    На Android читает из APK через android.activity.getAssets().
    На десктопе копирует из локальной папки IMAGES_DIR.
    """
    STORAGE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    if IS_ANDROID:
        from android.activity import getAssets
        assets = getAssets()
        try:
            image_files = assets.list('images')
        except Exception:
            return

        for filename in image_files:
            dest_path = STORAGE_IMAGES_DIR / filename
            if not dest_path.exists():
                with assets.open(f'images/{filename}') as src:
                    with open(dest_path, 'wb') as dst:
                        dst.write(src.read())
    else:
        if IMAGES_DIR.exists():
            for file_path in IMAGES_DIR.iterdir():
                if file_path.is_file():
                    dest_path = STORAGE_IMAGES_DIR / file_path.name
                    if not dest_path.exists():
                        shutil.copy2(file_path, dest_path)


def image(filename: str) -> str:
    """
    Возвращает абсолютный путь к изображению.
    На Android изображения предварительно копируются в STORAGE_IMAGES_DIR.
    На десктопе используется исходная папка assets/images.
    """
    if IS_ANDROID:
        return str(STORAGE_IMAGES_DIR / filename)
    else:
        return str(IMAGES_DIR / filename)


_copy_assets_to_storage()