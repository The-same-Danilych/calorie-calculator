"""
Главный модуль приложения CalorieTracker.
Определяет класс приложения и настраивает экраны.
"""
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivymd.app import MDApp

from ui.splash_screen import SplashScreen
from ui.onboarding.onboarding import OnboardingFlow
from ui.main_screen.home_screen import HomeScreen
from ui.main_screen.widgets.add_food_screen import AddFoodScreen
from ui.main_screen.widgets.analysis_screen import AnalysisScreen
from ui.main_screen.widgets.edit_profile_screen import EditProfileScreen

TRANSITION_DURATION = 0.35
DESKTOP_WINDOW_SIZE = (400, 700)


class CalorieApp(MDApp):
    """Главное приложение для учёта калорий."""

    def build(self) -> ScreenManager:
        """Инициализирует и возвращает корневой виджет — ScreenManager 
                            со всеми экранами.
        """
        self._configure_window_size()
        sm = self._create_screen_manager()
        self._add_screens(sm)
        sm.current = "splash"
        return sm

    def _configure_window_size(self) -> None:
        """
        Устанавливает фиксированный размер окна на десктопе
        для удобства отладки.
        """
        if platform not in ("android"):
            Window.size = DESKTOP_WINDOW_SIZE

    def _create_screen_manager(self) -> ScreenManager:
        """Создаёт менеджер экранов с заданным переходом."""
        return ScreenManager(transition=FadeTransition(
            duration=TRANSITION_DURATION
        ))

    def _add_screens(self, sm: ScreenManager) -> None:
        """Добавляет все экраны приложения в менеджер."""
        screens = [
            SplashScreen(name="splash"),
            OnboardingFlow(name="onboarding"),
            HomeScreen(name="home"),
            AddFoodScreen(name="add_food"),
            AnalysisScreen(name="analysis"),
            EditProfileScreen(name="edit_profile"),
        ]
        for screen in screens:
            sm.add_widget(screen)


if __name__ == "__main__":
    CalorieApp().run()
