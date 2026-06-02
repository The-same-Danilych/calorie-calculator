"""Экран выбора цели (снижение/поддержание/набор массы)."""

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.metrics import dp
from ui.onboarding.screens.base import OnboardingStepScreen
from ui.onboarding.screens.progress_bar import ProgressBarHeader

KV_GOAL = """
<GoalScreen>:
    MDBoxLayout:
        orientation: "vertical"
        size_hint: 1, 1
        padding: dp(24), 0, dp(24), dp(24)
        spacing: dp(20)
        md_bg_color: (1, 1, 1, 1)

        ProgressBarHeader:
            id: progress_header
            value: 0

        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: dp(56)
            MDIconButton:
                icon: "arrow-left"
                pos_hint: {"x": 0, "top": 1}
                size_hint: None, None
                size: dp(48), dp(48)
                theme_icon_color: "Custom"
                icon_color: (0, 0, 0, 1)
                on_release: root.go_back()

        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            spacing: dp(20)
            MDLabel:
                text: "Ваша цель"
                font_style: "Display"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]
            MDLabel:
                text: "Чего вы хотите достичь?"
                font_style: "Body"
                role: "large"
                halign: "center"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 0.7)

        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(16)
            size_hint_y: None
            height: dp(200)
            pos_hint: {"center_x": 0.5}
            padding: dp(16), 0
            MDSegmentedButton:
                id: goal_selector
                size_hint_x: 1
                size_hint_y: None
                height: dp(48)
                MDSegmentedButtonItem:
                    id: lose_item
                    text: "Сбросить вес"
                    on_release: root.on_goal_selected("lose")
                MDSegmentedButtonItem:
                    id: maintain_item
                    text: "Поддерживать"
                    on_release: root.on_goal_selected("maintain")
                MDSegmentedButtonItem:
                    id: gain_item
                    text: "Набрать массу"
                    on_release: root.on_goal_selected("gain")
            MDBoxLayout:
                id: info_card
                orientation: "vertical"
                size_hint_y: None
                height: dp(100)
                padding: dp(16), dp(12)
                md_bg_color: (0.95, 0.95, 0.95, 1)
                radius: [dp(12), dp(12), dp(12), dp(12)]
                MDLabel:
                    id: goal_title
                    text: ""
                    font_style: "Title"
                    role: "small"
                    size_hint_y: None
                    height: dp(28)
                    theme_text_color: "Custom"
                    text_color: (0, 0, 0, 1)
                MDLabel:
                    id: goal_desc
                    text: ""
                    font_style: "Body"
                    role: "medium"
                    size_hint_y: None
                    height: dp(48)
                    theme_text_color: "Secondary"
                    text_color: (0.4, 0.4, 0.4, 1)

        Widget:
            size_hint_y: 1

        MDButton:
            id: next_btn
            style: "filled"
            size_hint_x: 0.9
            size_hint_y: None
            height: dp(52)
            pos_hint: {"center_x": 0.5}
            theme_bg_color: "Custom"
            md_bg_color: (0, 0, 0, 1)
            disabled: True
            on_release: root.finish_onboarding()
            MDButtonText:
                text: "Завершить"
                theme_text_color: "Custom"
                text_color: (1, 1, 1, 1)
"""

Builder.load_string(KV_GOAL)


class GoalScreen(OnboardingStepScreen):
    """Экран выбора цели: похудение, поддержание, набор массы."""
    flow = ObjectProperty(None)
    show_progress = True
    selected_goal = None

    GOALS = {
        "lose": {
            "title": "Снижение веса",
            "desc": "Рекомендуем дефицит калорий 15-20% от нормы для плавного похудения"
        },
        "maintain": {
            "title": "Поддержание веса",
            "desc": "Сохраняйте текущую форму, придерживаясь нормы калорий"
        },
        "gain": {
            "title": "Набор массы",
            "desc": "Создайте профицит калорий 10-15% для качественного набора веса"
        }
    }

    def on_enter(self):
        super().on_enter()
        self.selected_goal = self.flow.data.get("goal", "maintain")
        self._set_goal_selector()
        self._update_info_card()
        self.ids.next_btn.disabled = False

    def _set_goal_selector(self):
        """Устанавливает активный элемент сегментированной кнопки."""
        items = {
            "lose": self.ids.lose_item,
            "maintain": self.ids.maintain_item,
            "gain": self.ids.gain_item
        }
        for goal_value, item in items.items():
            active = (self.selected_goal == goal_value)
            if hasattr(item, 'active'):
                item.active = active
            if hasattr(item, 'set_selected'):
                item.set_selected(active)

    def _update_info_card(self):
        """Обновляет текстовое описание выбранной цели."""
        if not self.selected_goal or self.selected_goal not in self.GOALS:
            return
        info = self.GOALS[self.selected_goal]
        self.ids.goal_title.text = info["title"]
        self.ids.goal_desc.text = info["desc"]

    def on_goal_selected(self, value: str):
        self.selected_goal = value
        self._set_goal_selector()
        self._update_info_card()
        self.save_to_flow()

    def validate(self) -> str | None:
        if not self.selected_goal:
            return "Выберите вашу цель"
        if self.selected_goal not in self.GOALS:
            return "Выберите корректную цель"
        return None

    def save_to_flow(self):
        if self.flow and self.selected_goal:
            self.flow.data["goal"] = self.selected_goal

    def finish_onboarding(self):
        """Завершает онбординг и сохраняет данные пользователя."""
        if self.flow:
            error = self.validate()
            if error:
                self.show_error(error)
                return
            self.save_to_flow()
            self.flow.finish()

    def go_back(self):
        if self.flow:
            self.flow.go_back()
