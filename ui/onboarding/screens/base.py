from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty
from kivy.animation import Animation


class OnboardingStepScreen(MDScreen):
    flow = ObjectProperty(None)
    _skip_validation = False
    show_progress = True

    def on_enter(self):
        super().on_enter()
        self._skip_validation = False
        if self.show_progress and self.flow:
            self.flow.update_progress_for_current_screen()

    def update_progress(self):
        if not self.show_progress:
            return

        for widget_id, widget in self.ids.items():
            if hasattr(widget, 'set_value'):
                current = self.flow.current_step_index()
                total = self.flow.total_steps()
                if total > 0:
                    target_value = (current / total) * 100
                    widget.set_value(target_value, animated=True)
                break

    def go_next(self):
        if self.flow:
            self.flow.go_next()

    def go_back(self):
        if self.flow:
            self._skip_validation = True
            self.flow.go_back()

    def validate(self) -> str | None:
        return None

    def save_to_flow(self):
        pass

    def on_leave(self):
        if self._skip_validation:
            return True
        error = self.validate()
        if error:
            self.show_error(error)
            return False
        self.save_to_flow()
        return True

    def show_error(self, message: str):
        from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
        MDSnackbar(
            MDSnackbarText(text=message),
            duration=2,
            pos_hint={"center_x": 0.5, "center_y": 0.1},
        ).open()
