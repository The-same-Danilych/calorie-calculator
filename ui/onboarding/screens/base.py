"""
Базовый класс для всех шагов онбординга
с общей логикой валидации и навигации.
"""

from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty


class OnboardingStepScreen(MDScreen):
    """
    Абстрактный шаг онбординга.
    Дочерние классы переопределяют validate() и save_to_flow().
    """
    flow = ObjectProperty(None)
    _skip_validation = False
    show_progress = True

    def on_enter(self):
        """
        Вызывается при входе на экран:
        сбрасывает флаг пропуска и обновляет прогресс.
        """
        super().on_enter()
        self._skip_validation = False
        if self.show_progress and self.flow:
            self.flow.update_progress_for_current_screen()

    def update_progress(self):
        """Обновляет значение прогресс-бара в соответствии с текущим шагом."""
        if not self.show_progress:
            return
        for widget in self.ids.values():
            if hasattr(widget, 'set_value'):
                current = self.flow.current_step_index()
                total = self.flow.total_steps()
                if total > 0:
                    target_value = (current / total) * 100
                    widget.set_value(target_value, animated=True)
                break

    def go_next(self):
        """Передаёт управление родительскому онбордингу для перехода вперёд."""
        if self.flow:
            self.flow.go_next()

    def go_back(self):
        """Передаёт управление родительскому онбордингу для возврата назад."""
        if self.flow:
            self._skip_validation = True
            self.flow.go_back()

    def validate(self) -> str | None:
        """
        Возвращает сообщение об ошибке, если данные невалидны.
        По умолчанию всегда валидно.
        """
        return None

    def save_to_flow(self):
        """Сохраняет данные текущего шага в общий словарь flow.data."""
        pass

    def on_leave(self):
        """
        Вызывается перед уходом с экрана.
        При возврате назад (skip_validation=True)
        пропускает проверку.
        Иначе вызывает validate() и, если есть ошибка, показывает её
        и возвращает False, блокируя переход.
        """
        if self._skip_validation:
            return True
        error = self.validate()
        if error:
            self.show_error(error)
            return False
        self.save_to_flow()
        return True

    def show_error(self, message: str):
        """Показывает всплывающее сообщение об ошибке."""
        from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
        MDSnackbar(
            MDSnackbarText(text=message),
            duration=2,
            pos_hint={"center_x": 0.5, "center_y": 0.1},
        ).open()
