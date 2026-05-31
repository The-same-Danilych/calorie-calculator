from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import SlideTransition
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from typing import Optional, Dict, Any

KV = """
<OnboardingFlow>:
    ScreenManager:
        id: inner_manager
"""

Builder.load_string(KV)


class OnboardingFlow(MDScreen):
    STEPS: tuple = ("greeting", "step_name", "step_gender", "step_birth",
                    "step_body", "step_activity", "step_goal")
    data = ObjectProperty({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = {
            "name": "",
            "gender": None,
            "years": None,
            "height_cm": None,
            "weight_kg": None,
            "activity": "moderate",
            "goal": "maintain",
        }

    def on_kv_post(self, base_widget):
        from ui.onboarding.screens.greetings import GreetingScreen
        from ui.onboarding.screens.name import NameScreen
        from ui.onboarding.screens.gender import GenderScreen
        from ui.onboarding.screens.years import YearScreen
        from ui.onboarding.screens.body import BodyScreen
        from ui.onboarding.screens.activity import ActivityScreen
        from ui.onboarding.screens.goal import GoalScreen

        inner = self.ids.inner_manager
        inner.transition = SlideTransition(duration=0.3)

        screens = [
            GreetingScreen(name="greeting"),
            NameScreen(name="step_name"),
            GenderScreen(name="step_gender"),
            YearScreen(name="step_birth"),
            BodyScreen(name="step_body"),
            ActivityScreen(name="step_activity"),
            GoalScreen(name="step_goal")
        ]

        for screen in screens:
            screen.flow = self
            inner.add_widget(screen)

        inner.current = "greeting"

    def update_progress_for_current_screen(self):
        inner = self.ids.inner_manager
        current_screen = inner.current_screen

        if inner.current == "greeting":
            return

        if hasattr(current_screen, 'update_progress'):
            current_screen.update_progress()

    def go_next(self):
        inner = self.ids.inner_manager
        current_screen = inner.current_screen

        if hasattr(current_screen, 'on_leave'):
            if not current_screen.on_leave():
                return

        idx = self.STEPS.index(inner.current)
        if idx < len(self.STEPS) - 1:
            inner.transition.direction = "left"
            inner.current = self.STEPS[idx + 1]
            self.update_progress_for_current_screen()

    def go_back(self):
        inner = self.ids.inner_manager
        current_screen = inner.current_screen

        if hasattr(current_screen, '_skip_validation'):
            current_screen._skip_validation = True

        idx = self.STEPS.index(inner.current)
        if idx > 0:
            inner.transition.direction = "right"
            inner.current = self.STEPS[idx - 1]
            self.update_progress_for_current_screen()

    def finish(self):
        from schemas.schemas import UserCreate
        from services.user_service import create_or_update_user_async

        def on_success(user):
            if self.manager.has_screen("home"):
                self.manager.current = "home"
            else:
                self.ids.inner_manager.current_screen.show_error(
                    "Данные сохранены.")

        def on_error(e):
            current_screen = self.ids.inner_manager.current_screen
            if hasattr(current_screen, "show_error"):
                current_screen.show_error(f"Ошибка сохранения: {e}")

        create_or_update_user_async(UserCreate(
            **self.data), on_success, on_error)

    def current_step_index(self) -> int:
        inner = self.ids.inner_manager
        if inner.current == "greeting":
            return 0
        idx = self.STEPS.index(inner.current)
        return idx

    def total_steps(self) -> int:
        return len(self.STEPS) - 1
