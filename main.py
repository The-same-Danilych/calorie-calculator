from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, FadeTransition


class CalorieApp(MDApp):
    def build(self):
        if platform not in ("android", "ios"):
            Window.size = (400, 700)

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Green"

        self.root = ScreenManager(transition=FadeTransition(duration=0.35))

        # ── Экраны ──────────────────────────────────────────────────
        from ui.splash_screen import SplashScreen
        self.root.add_widget(SplashScreen(name="splash"))

        from ui.onboarding.onboarding import OnboardingFlow
        self.root.add_widget(OnboardingFlow(name="onboarding"))

        from ui.main_screen.home_screen import HomeScreen
        self.root.add_widget(HomeScreen(name="home"))

        from ui.main_screen.add_food_screen import AddFoodScreen
        self.root.add_widget(AddFoodScreen(name="add_food"))

        self.root.current = "splash"
        return self.root


if __name__ == "__main__":
    CalorieApp().run()