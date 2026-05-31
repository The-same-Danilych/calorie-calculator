from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty, ColorProperty
from kivy.animation import Animation
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard

KV_MEAL = """
<MealSection>:
    orientation: "vertical"
    size_hint_y: None
    height: self.minimum_height
    spacing: 0

    # ── Заголовок приёма ──────────────────────────────────────────
    MDCard:
        size_hint_y: None
        height: dp(64)
        style: "elevated"
        elevation: 1
        radius: [dp(16), dp(16), 0, 0] if root.expanded else [dp(16)]
        padding: [dp(16), 0, dp(8), 0]
        md_bg_color: 1, 1, 1, 1
        ripple_behavior: True
        on_release: root.toggle_expand()

        MDBoxLayout:
            orientation: "horizontal"
            spacing: dp(12)

            # Иконка приёма
            MDBoxLayout:
                size_hint: None, None
                size: dp(40), dp(40)
                radius: [dp(12)]
                md_bg_color: root.icon_bg_color
                pos_hint: {"center_y": 0.5}

                MDLabel:
                    text: root.icon_emoji
                    font_size: dp(20)
                    halign: "center"
                    valign: "center"

            # Название + ккал
            MDBoxLayout:
                orientation: "vertical"
                size_hint_x: 1
                spacing: dp(2)
                pos_hint: {"center_y": 0.5}

                MDLabel:
                    text: root.meal_title
                    font_style: "Title"
                    role: "small"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 0.9
                    size_hint_y: None
                    height: dp(22)

                MDLabel:
                    text: root.summary_text
                    font_style: "Label"
                    role: "medium"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 0.45
                    size_hint_y: None
                    height: dp(18)

            # Стрелка
            MDIconButton:
                id: chevron
                icon: "chevron-up" if root.expanded else "chevron-down"
                size_hint: None, None
                size: dp(36), dp(36)
                pos_hint: {"center_y": 0.5}
                theme_icon_color: "Custom"
                icon_color: 0, 0, 0, 0.3
                on_release: root.toggle_expand()

    # ── Тело с продуктами ─────────────────────────────────────────
    MDCard:
        id: body_card
        size_hint_y: None
        height: 0
        opacity: 0
        style: "elevated"
        elevation: 1
        radius: [0, 0, dp(16), dp(16)]
        md_bg_color: 1, 1, 1, 1
        padding: 0
        overflow: "hidden"

        MDBoxLayout:
            id: entries_box
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height

        # Кнопка «Добавить»
        MDBoxLayout:
            size_hint_y: None
            height: dp(44)
            padding: [dp(16), 0, dp(16), 0]

            MDButton:
                style: "text"
                size_hint_x: None
                width: dp(160)
                height: dp(36)
                pos_hint: {"center_y": 0.5}
                on_release: root.on_add_pressed()

                MDButtonIcon:
                    icon: "plus"
                    theme_icon_color: "Custom"
                    icon_color: 0.18, 0.49, 0.31, 1

                MDButtonText:
                    text: "Добавить"
                    theme_text_color: "Custom"
                    text_color: 0.18, 0.49, 0.31, 1
"""

Builder.load_string(KV_MEAL)


class MealSection(MDBoxLayout):
    meal_key = StringProperty("breakfast")     # breakfast | lunch | dinner | snack
    meal_title = StringProperty("Завтрак")
    icon_emoji = StringProperty("🌅")
    icon_bg_color = ColorProperty([1, 0.95, 0.88, 1])
    expanded = BooleanProperty(True)
    total_calories = NumericProperty(0)
    entry_count = NumericProperty(0)
    on_add_callback = ObjectProperty(None, allownone=True)
    on_delete_callback = ObjectProperty(None, allownone=True)

    # ------------------------------------------------------------------ #
    _BODY_ITEM_H = 52   # dp высота одной строки
    _ADD_BTN_H   = 44   # dp кнопка «Добавить»

    @property
    def summary_text(self) -> str:
        if self.entry_count == 0:
            return "пусто"
        return f"{self.total_calories:.0f} ккал · {self.entry_count} блюда"

    # ------------------------------------------------------------------ #
    def toggle_expand(self):
        self.expanded = not self.expanded
        self._animate_body()

    def _target_body_height(self) -> float:
        if not self.expanded:
            return 0
        rows = len(self.ids.entries_box.children)
        return dp(rows * self._BODY_ITEM_H + self._ADD_BTN_H)

    def _animate_body(self):
        body = self.ids.body_card
        target_h = self._target_body_height()
        target_op = 1.0 if self.expanded else 0.0
        Animation.cancel_all(body)
        Animation(height=target_h, opacity=target_op,
                  duration=0.25, t="out_cubic").start(body)

    # ------------------------------------------------------------------ #
    def set_entries(self, entries: list):
        """entries: list[DiaryEntry ORM-объектов или dict]"""
        from ui.main_screen.widgets.food_entry_row import FoodEntryRow

        box = self.ids.entries_box
        box.clear_widgets()

        total_cal = 0
        for e in entries:
            # Поддержка и ORM-объекта и dict
            if isinstance(e, dict):
                eid      = e.get("id", 0)
                name     = e.get("food_name", "—")
                grams    = e.get("grams", 0)
                calories = e.get("calories", 0)
            else:
                eid      = e.id
                name     = e.food_item.name if e.food_item else "—"
                grams    = e.grams
                calories = e.calories

            row = FoodEntryRow(
                entry_id=eid,
                food_name=name,
                grams=grams,
                calories=calories,
                on_delete_callback=self.on_delete_callback,
            )
            box.add_widget(row)
            total_cal += calories

        self.total_calories = total_cal
        self.entry_count = len(entries)

        if self.expanded:
            # Пересчитать высоту сразу (без анимации, т.к. только заполнились данные)
            body = self.ids.body_card
            body.height = self._target_body_height()
            body.opacity = 1.0

    # ------------------------------------------------------------------ #
    def on_add_pressed(self):
        if self.on_add_callback:
            self.on_add_callback(self.meal_key)


# ─── Нужен импорт ColorProperty ───────────────────────────────────────── #
