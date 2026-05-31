from pathlib import Path
import sys

BASE_DIR = Path(__file__).parent.resolve()


def _is_android() -> bool:
    try:
        from android.storage import app_storage_path  # type: ignore
        return True
    except ImportError:
        return False


def _is_ios() -> bool:
    return sys.platform == "ios"


IS_ANDROID = "android" in sys.modules or _is_android()
IS_IOS = _is_ios()
IS_MOBILE = IS_ANDROID or IS_IOS
DEBUG = not IS_MOBILE


def _get_storage_dir() -> Path:
    if IS_ANDROID:
        from android.storage import app_storage_path  # type: ignore
        return Path(app_storage_path())
    elif IS_IOS:
        return Path(".") / "data"
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
FONTS_DIR = ASSETS_DIR / "fonts"

# Seed-данные
SEED_FILE = BASE_DIR / "database" / "seed_data" / "initial_food.json"


def image(filename: str) -> str:
    return str(IMAGES_DIR / filename)


def font(filename: str) -> str:
    return str(FONTS_DIR / filename)
