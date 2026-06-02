"""
Модуль для асинхронного выполнения фоновых задач с возвратом результата
в главный поток Kivy.
Использует ThreadPoolExecutor и Clock для безопасного обновления UI.
"""
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Callable, Optional, Any
from kivy.clock import Clock

MAX_WORKERS = 2
_executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)


def _schedule_callback(callback: Callable, arg: Any) -> None:
    """
    Планирует вызов callback с аргументом в главном потоке через Clock.
    Args:
        callback: функция, которая будет вызвана (принимает один аргумент)
        arg: аргумент, передаваемый в callback
    """
    Clock.schedule_once(lambda dt, a=arg: callback(a), 0)


def run_in_background(
    target: Callable,
    on_success: Optional[Callable[[Any], None]] = None,
    on_error: Optional[Callable[[Exception], None]] = None
) -> None:
    """
    Запускает функцию target в фоновом потоке.

    Args:
        target: функция, выполняемая в потоке (не принимает аргументов)
        on_success: вызывается в главном потоке с результатом target 
                    (если нет исключения)
        on_error: вызывается в главном потоке с исключением (если произошло)
    """
    def wrapped() -> None:
        try:
            result = target()
            if on_success:
                _schedule_callback(on_success, result)
        except Exception as e:
            if on_error:
                _schedule_callback(on_error, e)
            else:
                print(
                    f"[ERROR] Необработанное исключение в фоновой задаче: {e}",
                    flush=True)
                raise
    _executor.submit(wrapped)
