from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def _is_android() -> bool:
    try:
        import android
        return True
    except ImportError:
        return False


IS_ANDROID = _is_android()
IS_MOBILE = IS_ANDROID
DEBUG = not IS_MOBILE


def _get_storage_dir() -> Path:
    """
    Каталог для БД, логов и прочих файлов,
    которые должны быть доступны для записи.
    """
    if IS_ANDROID:
        from android.storage import app_storage_path

        storage = Path(app_storage_path())
        storage.mkdir(parents=True, exist_ok=True)
        return storage

    storage = BASE_DIR / "data"
    storage.mkdir(parents=True, exist_ok=True)
    return storage


STORAGE_DIR = _get_storage_dir()

DB_PATH = STORAGE_DIR / "calories.db"
DB_URL = f"sqlite:///{DB_PATH}"
LOG_FILE = STORAGE_DIR / "app.log"


ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"

SEED_FILE = (
    BASE_DIR
    / "database"
    / "seed_data"
    / "initial_food.json"
)


def image(filename: str) -> str:
    """
    Возвращает путь к изображению.

    Пример:
        image("apple.png")
    """
    return str(IMAGES_DIR / filename)