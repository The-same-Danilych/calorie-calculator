# utils/async_db.py
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Callable, Any
from kivy.clock import Clock

_executor = ThreadPoolExecutor(max_workers=2)


def run_in_background(func: Callable, on_success: Callable = None, on_error: Callable = None) -> None:
    """
    Запускает функцию func в фоновом потоке.
    Результат или исключение передаются в главный поток через Clock.
    """
    def wrapped():
        try:
            result = func()
            if on_success:
                Clock.schedule_once(lambda dt: on_success(result), 0)
        except Exception as e:
            if on_error:
                Clock.schedule_once(lambda dt: on_error(e), 0)
            else:
                raise
    _executor.submit(wrapped)
