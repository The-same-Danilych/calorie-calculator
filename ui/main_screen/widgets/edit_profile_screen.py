"""Экран редактирования профиля: вес, цель, уровень активности."""

from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from services.user_service import update_user_goals_sync, get_user_async
from utils.async_db import run_in_background
from database.models import GoalType, ActivityLevel

KV_EDIT_PROFILE = """
<EditProfileScreen>:
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: (1, 1, 1, 1)

        MDTopAppBar:
            title: "Редактировать профиль"
            elevation: 0
            md_bg_color: (1, 1, 1, 1)
            left_action_items: [["arrow-left", lambda x: root.go_back()]]

        MDScrollView:
            do_scroll_x: False
            bar_width: dp(4)
            bar_color: (0, 0, 0, 0.3)
            bar_inactive_color: (0, 0, 0, 0.1)

            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(15)
                padding: dp(12)
                size_hint_y: None
                height: self.minimum_height

                MDTextField:
                    id: weight_input
                    mode: "outlined"
                    size_hint_x: 1
                    pos_hint: {"center_x": 0.5}
                    theme_line_color: "Custom"
                    line_color_normal: (0, 0, 0, 1)
                    line_color_focus: (0, 0, 0, 1)
                    input_filter: "float"
                    on_text: root.validate_weight()
                    MDTextFieldHintText:
                        text: "Вес (кг)"
                    MDTextFieldHelperText:
                        id: weight_helper
                        text: ""
                        mode: "on_error"

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
                    text_color: (0, 0, 0, 0.7)

                MDSegmentedButton:
                    id: goal_selector
                    size_hint_x: 1
                    size_hint_y: None
                    height: dp(48)
                    pos_hint: {"center_x": 0.5}
                    MDSegmentedButtonItem:
                        id: lose_item
                        on_release: root.on_goal_selected("lose")
                        MDSegmentButtonLabel:
                            text: "Сбросить"
                    MDSegmentedButtonItem:
                        id: maintain_item
                        on_release: root.on_goal_selected("maintain")
                        MDSegmentButtonLabel:
                            text: "Поддерживать"
                    MDSegmentedButtonItem:
                        id: gain_item
                        on_release: root.on_goal_selected("gain")
                        MDSegmentButtonLabel:
                            text: "Набрать"

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
                    text_color: (0, 0, 0, 0.7)

                MDScrollView:
                    size_hint_y: None
                    height: dp(250)
                    do_scroll_x: False
                    bar_width: dp(4)
                    bar_color: (0, 0, 0, 0.3)
                    bar_inactive_color: (0, 0, 0, 0.1)

                    MDBoxLayout:
                        id: activities_container
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(8)
                        padding: [0, dp(8), 0, dp(8)]

                MDButton:
                    style: "filled"
                    size_hint_x: 0.9
                    size_hint_y: None
                    height: dp(52)
                    pos_hint: {"center_x": 0.5}
                    theme_bg_color: "Custom"
                    md_bg_color: (0, 0, 0, 1)
                    on_release: root.save_changes()
                    MDButtonText:
                        text: "Сохранить"
                        theme_text_color: "Custom"
                        text_color: (1, 1, 1, 1)
"""

Builder.load_string(KV_EDIT_PROFILE)


class EditProfileScreen(MDScreen):
    """Экран для изменения веса, цели и уровня активности."""
    ACTIVITIES = {
        "sedentary": "Сидячий образ жизни\n[color=808080]Мало или совсем нет физических нагрузок, офисная работа[/color]",
        "light": "Лёгкая активность\n[color=808080]Лёгкие упражнения 1-3 дня в неделю, прогулки[/color]",
        "moderate": "Умеренная активность\n[color=808080]Умеренные нагрузки 3-5 дней в неделю, спорт 1-2 раза[/color]",
        "active": "Высокая активность\n[color=808080]Интенсивные нагрузки 6-7 дней в неделю, активная работа[/color]",
        "very_active": "Экстремальная активность\n[color=808080]Тяжёлая физическая работа или тренировки 2 раза в день[/color]"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None
        self.selected_goal = None
        self.selected_activity = None
        self._loading = False

    def on_enter(self):
        self._loading = True
        get_user_async(self.on_user_loaded)

    def on_user_loaded(self, user):
        self.user = user
        self._loading = False
        if not user:
            MDSnackbar(MDSnackbarText(text="Ошибка загрузки профиля"),
                       duration=2).open()
            self.go_back()
            return

        self.ids.weight_input.text = str(user.weight_kg)
        self.validate_weight()

        self.selected_goal = user.goal
        self._update_goal_selector_visual()

        self._create_activity_list()
        self.selected_activity = user.activity
        self._set_selected_activity()

    def _update_goal_selector_visual(self):
        for item in [self.ids.lose_item,
                     self.ids.maintain_item,
                     self.ids.gain_item]:
            if hasattr(item, 'active'):
                item.active = False
            if hasattr(item, 'set_selected'):
                item.set_selected(False)
        target = None
        if self.selected_goal == "lose":
            target = self.ids.lose_item
        elif self.selected_goal == "maintain":
            target = self.ids.maintain_item
        elif self.selected_goal == "gain":
            target = self.ids.gain_item
        if target:
            if hasattr(target, 'active'):
                target.active = True
            if hasattr(target, 'set_selected'):
                target.set_selected(True)
        if hasattr(self.ids.goal_selector, 'refresh_view'):
            self.ids.goal_selector.refresh_view()

    def on_goal_selected(self, value: str):
        self.selected_goal = value
        self._update_goal_selector_visual()

    def _create_activity_list(self):
        container = self.ids.activities_container
        container.clear_widgets()
        for value, text in self.ACTIVITIES.items():
            row = MDBoxLayout(orientation="horizontal",
                              size_hint_y=None,
                              height=dp(70),
                              spacing=dp(12),
                              padding=[dp(8), dp(8), dp(8), dp(8)])
            checkbox = MDCheckbox(
                size_hint=(None, None), size=(dp(48), dp(48)), color_active=(0, 0, 0, 1),
                color_inactive=(0.5, 0.5, 0.5, 1), group="activity_group",
                on_release=lambda x, v=value: self.on_activity_selected(v)
            )
            label = MDLabel(
                text=text, markup=True,
                size_hint_x=1,
                size_hint_y=None,
                height=dp(54),
                theme_text_color="Custom", text_color=(0, 0, 0, 0.9),
                halign="left",
                valign="center"
            )
            row.add_widget(checkbox)
            row.add_widget(label)
            container.add_widget(row)

    def _set_selected_activity(self):
        container = self.ids.activities_container
        keys = list(self.ACTIVITIES.keys())
        for i, row in enumerate(container.children[::-1]):
            if i < len(keys):
                checkbox = row.children[1] if len(row.children) > 1 else None
                if checkbox and isinstance(checkbox, MDCheckbox):
                    checkbox.active = (keys[i] == self.selected_activity)

    def on_activity_selected(self, value: str):
        self.selected_activity = value

    def validate_weight(self) -> bool:
        try:
            weight_text = self.ids.weight_input.text.strip().replace(",", ".")
            if not weight_text:
                self.ids.weight_helper.text = "Поле обязательно для заполнения"
                self.ids.weight_helper.mode = "on_error"
                return False
            weight = float(weight_text)
            if 20 <= weight <= 500:
                self.ids.weight_helper.text = ""
                self.ids.weight_helper.mode = "persistent"
                return True
            else:
                self.ids.weight_helper.text = "Вес должен быть от 20 до 500 кг"
                self.ids.weight_helper.mode = "on_error"
                return False
        except ValueError:
            self.ids.weight_helper.text = "Введите число (например, 75.5)"
            self.ids.weight_helper.mode = "on_error"
            return False

    def validate(self) -> str | None:
        if not self.validate_weight():
            return "Введите корректный вес (20–500 кг)"
        if not self.selected_goal or self.selected_goal not in [g.value for g in GoalType]:
            return "Выберите цель"
        if not self.selected_activity or self.selected_activity not in [a.value for a in ActivityLevel]:
            return "Выберите уровень активности"
        return None

    def save_changes(self):
        error = self.validate()
        if error:
            MDSnackbar(MDSnackbarText(text=error), duration=2).open()
            return

        weight_text = self.ids.weight_input.text.strip().replace(",", ".")
        new_weight = float(weight_text)
        new_goal = self.selected_goal
        new_activity = self.selected_activity

        def task():
            return update_user_goals_sync(self.user.id,
                                          new_weight,
                                          new_goal,
                                          new_activity)

        run_in_background(
            task,
            on_success=self.on_saved,
            on_error=lambda e: MDSnackbar(MDSnackbarText(text=f"Ошибка: {e}"),
                                          duration=2).open()
        )

    def on_saved(self, _):
        MDSnackbar(MDSnackbarText(text="Профиль обновлён"), duration=2).open()
        if self.manager and self.manager.has_screen("home"):
            home = self.manager.get_screen("home")
            home.load_data()
        self.go_back()

    def go_back(self):
        if self.manager and self.manager.has_screen("home"):
            self.manager.current = "home"
