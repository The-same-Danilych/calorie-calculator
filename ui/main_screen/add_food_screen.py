# ui/home/add_food_screen.py
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon

from services.food_service import search_food
from services.diary_service import add_diary_entry
from schemas.schemas import DiaryEntryCreate, FoodItemCreate
from utils.async_db import run_in_background

KV_ADD = """
<SuggestionItem>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(52)
    padding: [dp(16), 0, dp(16), 0]
    spacing: dp(8)
    ripple_behavior: True

    MDBoxLayout:
        orientation: "vertical"
        size_hint_x: 1
        spacing: dp(2)
        pos_hint: {"center_y": 0.5}

        MDLabel:
            text: root.food_name
            font_style: "Body"
            role: "medium"
            theme_text_color: "Custom"
            text_color: 0, 0, 0, 0.88
            size_hint_y: None
            height: dp(22)
            shorten: True
            shorten_from: "right"

        MDLabel:
            text: root.meta_text
            font_style: "Label"
            role: "medium"
            theme_text_color: "Custom"
            text_color: 0, 0, 0, 0.4
            size_hint_y: None
            height: dp(18)

    MDLabel:
        text: root.cal_text
        font_style: "Label"
        role: "large"
        size_hint_x: None
        width: dp(64)
        halign: "right"
        valign: "center"
        theme_text_color: "Custom"
        text_color: 0.18, 0.49, 0.31, 1


<AddFoodScreen>:
    MDBoxLayout:
        orientation: "vertical"
        size_hint: 1, 1
        md_bg_color: 0.96, 0.96, 0.94, 1

        # ── AppBar ─────────────────────────────────────────────────
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: dp(56)
            padding: [dp(8), dp(4), dp(16), dp(4)]
            spacing: dp(4)
            md_bg_color: 1, 1, 1, 1

            MDIconButton:
                icon: "arrow-left"
                size_hint: None, None
                size: dp(48), dp(48)
                pos_hint: {"center_y": 0.5}
                theme_icon_color: "Custom"
                icon_color: 0, 0, 0, 1
                on_release: root.go_back()

            MDLabel:
                id: screen_title
                text: "Добавить продукт"
                font_style: "Title"
                role: "medium"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                valign: "center"

        MDDivider:
            size_hint_y: None
            height: dp(1)

        # ── Тело ──────────────────────────────────────────────────
        MDScrollView:
            do_scroll_x: False
            bar_width: 0

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(16), dp(16), dp(16), dp(100)]
                spacing: dp(12)

                # ── Поиск ─────────────────────────────────────────
                MDTextField:
                    id: search_field
                    mode: "outlined"
                    size_hint_x: 1
                    theme_line_color: "Custom"
                    line_color_normal: 0, 0, 0, 0.3
                    line_color_focus: 0, 0, 0, 1
                    on_text: root.on_search_text(self.text)

                    MDTextFieldLeadingIcon:
                        icon: "magnify"
                        theme_icon_color: "Custom"
                        icon_color: 0, 0, 0, 0.4

                    MDTextFieldHintText:
                        text: "Поиск продукта..."

                # ── Подсказки из БД ───────────────────────────────
                MDCard:
                    id: suggestions_card
                    style: "elevated"
                    elevation: 1
                    radius: [dp(12)]
                    size_hint_y: None
                    height: 0
                    opacity: 0
                    padding: 0
                    md_bg_color: 1, 1, 1, 1
                    overflow: "hidden"

                    MDBoxLayout:
                        id: suggestions_box
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height

                # ── Карточка: данные продукта ─────────────────────
                MDCard:
                    style: "elevated"
                    elevation: 1
                    radius: [dp(16)]
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(16), dp(16), dp(16), dp(16)]
                    md_bg_color: 1, 1, 1, 1

                    MDBoxLayout:
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(16)

                        MDLabel:
                            text: "Продукт"
                            font_style: "Label"
                            role: "large"
                            theme_text_color: "Custom"
                            text_color: 0, 0, 0, 0.4
                            size_hint_y: None
                            height: dp(18)

                        MDTextField:
                            id: name_field
                            mode: "outlined"
                            size_hint_x: 1
                            theme_line_color: "Custom"
                            line_color_normal: 0, 0, 0, 0.3
                            line_color_focus: 0, 0, 0, 1

                            MDTextFieldHintText:
                                text: "Название"

                        MDTextField:
                            id: grams_field
                            mode: "outlined"
                            size_hint_x: 1
                            input_filter: "float"
                            theme_line_color: "Custom"
                            line_color_normal: 0, 0, 0, 0.3
                            line_color_focus: 0, 0, 0, 1
                            on_text: root.on_grams_changed(self.text)

                            MDTextFieldHintText:
                                text: "Количество (г)"

                        # Приём пищи
                        MDLabel:
                            text: "Приём пищи"
                            font_style: "Label"
                            role: "large"
                            theme_text_color: "Custom"
                            text_color: 0, 0, 0, 0.4
                            size_hint_y: None
                            height: dp(18)

                        MDBoxLayout:
                            id: meal_selector
                            orientation: "horizontal"
                            size_hint_y: None
                            height: dp(40)
                            spacing: dp(8)

                # ── Карточка: КБЖУ на 100 г ───────────────────────
                MDCard:
                    style: "elevated"
                    elevation: 1
                    radius: [dp(16)]
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(16), dp(16), dp(16), dp(16)]
                    md_bg_color: 1, 1, 1, 1

                    MDBoxLayout:
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(12)

                        MDLabel:
                            text: "КБЖУ на 100 г"
                            font_style: "Label"
                            role: "large"
                            theme_text_color: "Custom"
                            text_color: 0, 0, 0, 0.4
                            size_hint_y: None
                            height: dp(18)

                        MDGridLayout:
                            cols: 2
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: [dp(12), dp(12)]

                            MDTextField:
                                id: cal_field
                                mode: "outlined"
                                input_filter: "float"
                                theme_line_color: "Custom"
                                line_color_normal: 0, 0, 0, 0.3
                                line_color_focus: 0, 0, 0, 1
                                on_text: root.on_macro_changed()

                                MDTextFieldHintText:
                                    text: "Калории (ккал)"

                            MDTextField:
                                id: protein_field
                                mode: "outlined"
                                input_filter: "float"
                                theme_line_color: "Custom"
                                line_color_normal: 0, 0, 0, 0.3
                                line_color_focus: 0, 0, 0, 1
                                on_text: root.on_macro_changed()

                                MDTextFieldHintText:
                                    text: "Белки (г)"

                            MDTextField:
                                id: fat_field
                                mode: "outlined"
                                input_filter: "float"
                                theme_line_color: "Custom"
                                line_color_normal: 0, 0, 0, 0.3
                                line_color_focus: 0, 0, 0, 1
                                on_text: root.on_macro_changed()

                                MDTextFieldHintText:
                                    text: "Жиры (г)"

                            MDTextField:
                                id: carbs_field
                                mode: "outlined"
                                input_filter: "float"
                                theme_line_color: "Custom"
                                line_color_normal: 0, 0, 0, 0.3
                                line_color_focus: 0, 0, 0, 1
                                on_text: root.on_macro_changed()

                                MDTextFieldHintText:
                                    text: "Углеводы (г)"

                # ── Итого для порции ──────────────────────────────
                MDCard:
                    id: preview_card
                    style: "elevated"
                    elevation: 1
                    radius: [dp(16)]
                    size_hint_y: None
                    height: 0
                    opacity: 0
                    padding: [dp(16), dp(12), dp(16), dp(12)]
                    md_bg_color: 1, 1, 1, 1
                    overflow: "hidden"

                    MDBoxLayout:
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(8)

                        MDLabel:
                            text: "Итого для порции"
                            font_style: "Label"
                            role: "large"
                            theme_text_color: "Custom"
                            text_color: 0, 0, 0, 0.4
                            size_hint_y: None
                            height: dp(18)

                        MDBoxLayout:
                            id: preview_row
                            orientation: "horizontal"
                            size_hint_y: None
                            height: dp(48)

        # ── Кнопка «Добавить в дневник» ────────────────────────────
        MDBoxLayout:
            size_hint_y: None
            height: dp(84)
            padding: [dp(20), dp(16), dp(20), dp(16)]
            md_bg_color: 0.96, 0.96, 0.94, 1

            MDButton:
                id: submit_btn
                style: "filled"
                size_hint_x: 1
                size_hint_y: None
                height: dp(52)
                pos_hint: {"center_y": 0.5}
                theme_bg_color: "Custom"
                md_bg_color: 0, 0, 0, 1
                disabled: True
                on_release: root.submit()

                MDButtonText:
                    text: "Добавить в дневник"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
"""

Builder.load_string(KV_ADD)

# ───────────────────────────────────────────────────────────────────────── #
MEAL_LABELS = {
    "breakfast": "Завтрак",
    "lunch":     "Обед",
    "dinner":    "Ужин",
    "snack":     "Перекус",
}


class SuggestionItem(MDBoxLayout):
    food_name = StringProperty("")
    calories  = StringProperty("0")
    protein   = StringProperty("0")
    fat       = StringProperty("0")
    carbs     = StringProperty("0")
    food_id   = ObjectProperty(None, allownone=True)
    on_select_callback = ObjectProperty(None, allownone=True)

    @property
    def meta_text(self) -> str:
        return f"Б {self.protein} · Ж {self.fat} · У {self.carbs}  |  на 100 г"

    @property
    def cal_text(self) -> str:
        return f"{float(self.calories):.0f} ккал"

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.on_select_callback:
                self.on_select_callback(self)
            return True
        return super().on_touch_down(touch)


# ───────────────────────────────────────────────────────────────────────── #
class AddFoodScreen(MDScreen):
    """
    Экран добавления продукта.

    Использование:
        screen = AddFoodScreen(name="add_food")
        screen.open_for(meal_key="lunch", user_id=1, on_done=callback)
    """

    _search_event = None   # Clock-событие для debounce поиска

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._user_id       = 1
        self._meal_key      = "lunch"
        self._on_done       = None
        self._selected_food_id = None   # id FoodItem из БД если выбран
        self._meal_btns     = {}

    # ------------------------------------------------------------------ #
    def open_for(self, meal_key: str, user_id: int, on_done=None):
        """Настраивает экран перед показом."""
        self._user_id  = user_id
        self._meal_key = meal_key
        self._on_done  = on_done
        self._selected_food_id = None
        self._clear_form()
        self._build_meal_buttons()
        self._select_meal_btn(meal_key)

    # ── Строим чипы выбора приёма пищи ───────────────────────────── #
    def _build_meal_buttons(self):
        box = self.ids.meal_selector
        if self._meal_btns:
            return   # уже построено

        for key, label in MEAL_LABELS.items():
            btn = MDButton(
                MDButtonText(
                    text=label,
                    theme_text_color="Custom",
                    text_color=(0, 0, 0, 1),
                ),
                style="outlined",
                size_hint_x=None,
                size_hint_y=None,
                height=dp(36),
                theme_line_color="Custom",
                line_color_normal=(0, 0, 0, 0.3),
            )
            btn.bind(on_release=lambda _, k=key: self._select_meal_btn(k))
            self._meal_btns[key] = btn
            box.add_widget(btn)

    def _select_meal_btn(self, key: str):
        self._meal_key = key
        for k, btn in self._meal_btns.items():
            is_active = (k == key)
            btn.theme_bg_color = "Custom"
            btn.md_bg_color    = (0, 0, 0, 1) if is_active else (1, 1, 1, 0)
            text_widget = btn.children[0] if btn.children else None
            if text_widget:
                text_widget.text_color = (1, 1, 1, 1) if is_active else (0, 0, 0, 1)
        self._check_submit()

    # ── Поиск (debounce 300 мс) ───────────────────────────────────── #
    def on_search_text(self, text: str):
        if self._search_event:
            self._search_event.cancel()
        q = text.strip()
        if len(q) < 2:
            self._hide_suggestions()
            return
        self._search_event = Clock.schedule_once(
            lambda dt: self._do_search(q), 0.3
        )

    def _do_search(self, query: str):
        def task():
            return search_food(query, limit=7)

        run_in_background(task, self._on_search_result)

    def _on_search_result(self, items):
        from kivy.animation import Animation
        box  = self.ids.suggestions_box
        card = self.ids.suggestions_card
        box.clear_widgets()

        if not items:
            self._hide_suggestions()
            return

        for food in items:
            item = SuggestionItem(
                food_name=food.name,
                calories=str(food.calories),
                protein=str(food.protein),
                fat=str(food.fat),
                carbs=str(food.carbs),
                food_id=food.id,
                on_select_callback=self._on_suggestion_selected,
            )
            # Тонкая разделительная линия
            from kivymd.uix.divider import MDDivider
            box.add_widget(item)
            box.add_widget(MDDivider(size_hint_y=None, height=dp(1)))

        target_h = min(len(items), 5) * dp(52) + len(items) * dp(1)
        Animation.cancel_all(card)
        card.height  = target_h
        card.opacity = 1.0

    def _hide_suggestions(self):
        from kivy.animation import Animation
        card = self.ids.suggestions_card
        Animation.cancel_all(card)
        Animation(height=0, opacity=0, duration=0.15).start(card)

    def _on_suggestion_selected(self, item: "SuggestionItem"):
        """Заполняет форму данными выбранного продукта."""
        self.ids.search_field.text = item.food_name
        self.ids.name_field.text   = item.food_name
        self.ids.cal_field.text    = item.calories
        self.ids.protein_field.text = item.protein
        self.ids.fat_field.text    = item.fat
        self.ids.carbs_field.text  = item.carbs
        self._selected_food_id     = item.food_id

        if not self.ids.grams_field.text:
            self.ids.grams_field.text = "100"

        self._hide_suggestions()
        self.on_macro_changed()

    # ── Авто-заполнение со штрихкода ──────────────────────────────── #
    def fill_from_barcode(self, food_item):
        """Вызывается из экрана сканера после успешного поиска по штрихкоду."""
        self.ids.screen_title.text = "Штрихкод — продукт найден"
        self._on_suggestion_selected_obj(food_item)

    def _on_suggestion_selected_obj(self, food):
        """Заполняет форму из ORM FoodItem."""
        self.ids.name_field.text    = food.name
        self.ids.cal_field.text     = str(food.calories)
        self.ids.protein_field.text = str(food.protein)
        self.ids.fat_field.text     = str(food.fat)
        self.ids.carbs_field.text   = str(food.carbs)
        self._selected_food_id      = food.id
        if not self.ids.grams_field.text:
            self.ids.grams_field.text = "100"
        self.on_macro_changed()

    # ── Пересчёт порции ──────────────────────────────────────────── #
    def on_grams_changed(self, text: str):
        self.on_macro_changed()

    def on_macro_changed(self):
        from kivy.animation import Animation

        grams   = self._float(self.ids.grams_field.text)
        cal100  = self._float(self.ids.cal_field.text)
        prot100 = self._float(self.ids.protein_field.text)
        fat100  = self._float(self.ids.fat_field.text)
        carbs100= self._float(self.ids.carbs_field.text)

        card = self.ids.preview_card
        if grams > 0 and cal100 > 0:
            f = grams / 100
            self._update_preview(
                cal100 * f, prot100 * f, fat100 * f, carbs100 * f
            )
            Animation.cancel_all(card)
            card.height  = dp(80)
            card.opacity = 1.0
        else:
            Animation.cancel_all(card)
            Animation(height=0, opacity=0, duration=0.15).start(card)

        self._check_submit()

    def _update_preview(self, cal, prot, fat, carbs):
        row = self.ids.preview_row
        row.clear_widgets()
        defs = [
            ("ккал",   f"{cal:.0f}",   (0.18, 0.49, 0.31, 1)),
            ("белки",  f"{prot:.1f} г", (0.36, 0.50, 0.83, 1)),
            ("жиры",   f"{fat:.1f} г",  (0.83, 0.53, 0.36, 1)),
            ("углев.", f"{carbs:.1f} г",(0.32, 0.66, 0.47, 1)),
        ]
        for label, value, color in defs:
            col = MDBoxLayout(orientation="vertical", size_hint_x=1,
                              spacing=dp(2))
            col.add_widget(MDLabel(
                text=value,
                font_style="Title", role="small",
                halign="center", valign="center",
                theme_text_color="Custom", text_color=color,
                size_hint_y=None, height=dp(28),
            ))
            col.add_widget(MDLabel(
                text=label,
                font_style="Label", role="small",
                halign="center", valign="center",
                theme_text_color="Custom", text_color=(0, 0, 0, 0.4),
                size_hint_y=None, height=dp(16),
            ))
            row.add_widget(col)

    # ── Валидация и сабмит ───────────────────────────────────────── #
    def _check_submit(self):
        ok = bool(
            self.ids.name_field.text.strip()
            and self._float(self.ids.grams_field.text) > 0
            and self._float(self.ids.cal_field.text) >= 0
            and self._meal_key
        )
        self.ids.submit_btn.disabled = not ok

    def submit(self):
        name  = self.ids.name_field.text.strip()
        grams = self._float(self.ids.grams_field.text)
        cal   = self._float(self.ids.cal_field.text)
        prot  = self._float(self.ids.protein_field.text)
        fat   = self._float(self.ids.fat_field.text)
        carbs = self._float(self.ids.carbs_field.text)

        if not name or grams <= 0:
            self._show_error("Укажите название и количество граммов")
            return

        # Если продукт выбран из БД — используем его id напрямую
        if self._selected_food_id is not None:
            self._save_entry(self._selected_food_id, grams)
        else:
            # Создаём новый кастомный продукт, потом запись
            self._create_food_and_save(name, cal, prot, fat, carbs, grams)

    def _save_entry(self, food_id: int, grams: float):
        user_id  = self._user_id
        meal_key = self._meal_key

        def task():
            return add_diary_entry(user_id, DiaryEntryCreate(
                food_item_id=food_id,
                grams=grams,
                meal_type=meal_key,
            ))

        run_in_background(task, self._on_saved, self._on_error)

    def _create_food_and_save(self, name, cal, prot, fat, carbs, grams):
        from services.food_service import add_food
        user_id  = self._user_id
        meal_key = self._meal_key

        def task():
            food = add_food(FoodItemCreate(
                name=name,
                calories=cal,
                protein=prot,
                fat=fat,
                carbs=carbs,
                is_custom=True,
            ))
            return add_diary_entry(user_id, DiaryEntryCreate(
                food_item_id=food.id,
                grams=grams,
                meal_type=meal_key,
            ))

        run_in_background(task, self._on_saved, self._on_error)

    def _on_saved(self, entry):
        self._clear_form()
        if self._on_done:
            self._on_done(entry)
        self.go_back()

    def _on_error(self, e):
        self._show_error(f"Ошибка: {e}")

    # ── Навигация ─────────────────────────────────────────────────── #
    def go_back(self):
        if self.manager and self.manager.has_screen("home"):
            self.manager.current = "home"

    # ── Утилиты ───────────────────────────────────────────────────── #
    def _clear_form(self):
        for field_id in ("search_field", "name_field", "grams_field",
                         "cal_field", "protein_field", "fat_field", "carbs_field"):
            self.ids[field_id].text = ""
        self._selected_food_id = None
        self._hide_suggestions()
        from kivy.animation import Animation
        card = self.ids.preview_card
        card.height  = 0
        card.opacity = 0
        self.ids.submit_btn.disabled = True
        self.ids.screen_title.text   = "Добавить продукт"

    @staticmethod
    def _float(text: str) -> float:
        try:
            return max(0.0, float(text.strip().replace(",", ".")))
        except (ValueError, AttributeError):
            return 0.0

    def _show_error(self, msg: str):
        from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
        MDSnackbar(
            MDSnackbarText(text=msg),
            duration=2.5,
            pos_hint={"center_x": 0.5, "center_y": 0.1},
        ).open()