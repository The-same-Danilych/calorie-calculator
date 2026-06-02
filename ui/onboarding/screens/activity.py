"""Экран выбора физической активности во время онбординга."""

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.metrics import dp
from ui.onboarding.screens.base import OnboardingStepScreen
from ui.onboarding.screens.progress_bar import ProgressBarHeader

KV_ACTIVITY = """
<ActivityScreen>:
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
                text: "Ваша физическая активность"
                font_style: "Display"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]
            MDLabel:
                text: "Выберите уровень, который лучше всего описывает ваш образ жизни"
                font_style: "Body"
                role: "large"
                halign: "center"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 0.7)

        MDScrollView:
            size_hint_y: 1
            do_scroll_x: False
            bar_width: dp(4)
            bar_color: (0, 0, 0, 0.3)
            bar_inactive_color: (0, 0, 0, 0.1)
            MDBoxLayout:
                id: buttons_container
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)
                padding: [0, dp(8), 0, dp(8)]

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
            on_release: root.go_next()
            MDButtonText:
                text: "Продолжить"
                theme_text_color: "Custom"
                text_color: (1, 1, 1, 1)
"""

Builder.load_string(KV_ACTIVITY)


class ActivityScreen(OnboardingStepScreen):
    """Экран выбора уровня физической активности."""
    flow = ObjectProperty(None)
    show_progress = True
    selected_activity = None

    ACTIVITIES = {
        "sedentary": "Сидячий образ жизни\n[color=808080]Мало или совсем нет физических нагрузок, офисная работа[/color]",
        "light": "Лёгкая активность\n[color=808080]Лёгкие упражнения 1-3 дня в неделю, прогулки[/color]",
        "moderate": "Умеренная активность\n[color=808080]Умеренные нагрузки 3-5 дней в неделю, спорт 1-2 раза[/color]",
        "active": "Высокая активность\n[color=808080]Интенсивные нагрузки 6-7 дней в неделю, активная работа[/color]",
        "very_active": "Экстремальная активность\n[color=808080]Тяжёлая физическая работа или тренировки 2 раза в день[/color]"
    }

    def on_enter(self):
        """
        При входе создаём список вариантов
        и восстанавливаем сохранённое значение.
        """
        super().on_enter()
        self._create_activity_list()
        saved = self.flow.data.get("activity", "moderate")
        self.selected_activity = saved
        self._set_selected_checkbox(saved)
        if self.selected_activity:
            self.ids.next_btn.disabled = False

    def _create_activity_list(self):
        """
        Динамически создаёт чекбоксы
        с подписями для каждого уровня активности.
        """
        container = self.ids.buttons_container
        container.clear_widgets()
        for value, text in self.ACTIVITIES.items():
            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(70),
                spacing=dp(12),
                padding=[dp(8), dp(8), dp(8), dp(8)]
            )
            checkbox = MDCheckbox(
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                color_active=(0, 0, 0, 1),
                color_inactive=(0.5, 0.5, 0.5, 1),
                group="activity_group",
                on_release=lambda x, v=value: self.on_activity_selected(v)
            )
            label = MDLabel(
                text=text,
                markup=True,
                size_hint_x=1,
                size_hint_y=None,
                height=dp(54),
                theme_text_color="Custom",
                text_color=(0, 0, 0, 0.9),
                halign="left",
                valign="center"
            )
            row.add_widget(checkbox)
            row.add_widget(label)
            container.add_widget(row)

    def _set_selected_checkbox(self, value: str):
        """
        Устанавливает активный чекбокс в соответствии
        с выбранным значением.
        """
        container = self.ids.buttons_container
        keys = list(self.ACTIVITIES.keys())
        for i, row in enumerate(container.children[::-1]):
            if i < len(keys):
                checkbox = row.children[1] if len(row.children) > 1 else None
                if checkbox and isinstance(checkbox, MDCheckbox):
                    checkbox.active = (keys[i] == value)

    def on_activity_selected(self, value: str):
        """Обработчик выбора уровня активности."""
        self.selected_activity = value
        self.save_to_flow()
        self.ids.next_btn.disabled = False

    def validate(self) -> str | None:
        """Проверяет, что выбран корректный уровень."""
        if not self.selected_activity:
            return "Выберите уровень физической активности"
        if self.selected_activity not in self.ACTIVITIES:
            return "Выберите корректный уровень активности"
        return None

    def save_to_flow(self):
        """Сохраняет выбранный уровень в общий словарь данных."""
        if self.flow and self.selected_activity:
            self.flow.data["activity"] = self.selected_activity

    def go_next(self):
        """Переход к следующему шагу после валидации."""
        if self.flow:
            error = self.validate()
            if error:
                self.show_error(error)
                return
            self.save_to_flow()
            self.flow.go_next()

    def go_back(self):
        """Возврат к предыдущему шагу."""
        if self.flow:
            self.flow.go_back()
