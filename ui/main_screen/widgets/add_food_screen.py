"""
Экран добавления продукта в дневник: поиск,
ручной ввод КБЖУ, выбор приёма пищи.
"""

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from kivymd.uix.list import (MDListItem,
                             MDListItemHeadlineText,
                             MDListItemSupportingText,
                             MDListItemTrailingIcon)
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.divider import MDDivider
from services.food_service import search_food, get_food_item
from services.diary_service import (add_diary_entry,
                                    get_diary_entry,
                                    update_diary_entry,
                                    )
from schemas.schemas import DiaryEntryCreate, FoodItemCreate, DiaryEntryUpdate
from utils.async_db import run_in_background

KV_ADD = """
<AddFoodScreen>:
    MDBoxLayout:
        orientation: "vertical"
        size_hint: 1, 1
        md_bg_color: 0.96, 0.96, 0.94, 1

        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: dp(56)
            padding: [dp(8), dp(4), dp(16), dp(4)]
            spacing: dp(4)
            md_bg_color: 1, 1, 1, 1

            MDButton:
                size_hint: None, None
                size: dp(48), dp(48)
                pos_hint: {"center_y": 0.5}
                style: "text"
                on_release: root.go_back()
                MDButtonIcon:
                    icon: "arrow-left"
                    theme_icon_color: "Custom"
                    icon_color: 0, 0, 0, 1

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

        MDRelativeLayout:
            size_hint_y: 1

            MDScrollView:
                id: scroll_view
                do_scroll_x: False
                bar_width: 0

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(16), dp(16), dp(16), dp(100)]
                    spacing: dp(12)

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
                                helper_text: "Введите название продукта"
                                helper_text_mode: "on_focus"
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
                                helper_text: "Количество в граммах (1-5000)"
                                helper_text_mode: "on_focus"
                                MDTextFieldHintText:
                                    text: "Количество (г)"

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
                                    helper_text: "0-9000 ккал"
                                    helper_text_mode: "on_focus"
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
                                    helper_text: "0-100 г"
                                    helper_text_mode: "on_focus"
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
                                    helper_text: "0-100 г"
                                    helper_text_mode: "on_focus"
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
                                    helper_text: "0-100 г"
                                    helper_text_mode: "on_focus"
                                    MDTextFieldHintText:
                                        text: "Углеводы (г)"

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

            MDCard:
                id: suggestions_card
                style: "elevated"
                elevation: 4
                radius: [dp(12)]
                size_hint: 1, None
                height: 0
                opacity: 0
                padding: 0
                md_bg_color: 1, 1, 1, 1
                overflow: "hidden"
                pos_hint: {"top": 1.0, "center_x": 0.5}

                MDScrollView:
                    id: suggestions_scroll
                    do_scroll_x: False
                    bar_width: dp(4)

                    MDBoxLayout:
                        id: suggestions_box
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height

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
                pos_hint: {"center_y": 0.5, "center_x": 0.5}
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

MEAL_LABELS = {
    "breakfast": "Завтрак",
    "lunch": "Обед",
    "dinner": "Ужин",
    "snack": "Перекус",
}


class AddFoodScreen(MDScreen):
    """Экран добавления продукта (с поиском и ручным вводом)."""
    _search_event = None

    GRAMS_MIN = 1
    GRAMS_MAX = 5000
    CALORIES_MAX = 9000
    MACRO_MAX = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._user_id = 1
        self._meal_key = "lunch"
        self._on_done = None
        self._selected_food_id = None
        self._meal_btns = {}
        self._edit_entry_id = None

    def open_for(self, meal_key: str, user_id: int, on_done=None):
        """
        Настраивает экран для добавления: приём пищи, ID пользователя,
        колбэк после сохранения.
        """
        self._user_id = user_id
        self._meal_key = meal_key
        self._on_done = on_done
        self._selected_food_id = None
        self._edit_entry_id = None
        self._clear_form()
        self._build_meal_buttons()
        self._select_meal_btn(meal_key)
        self.ids.screen_title.text = "Добавить продукт"
        self.ids.submit_btn.children[0].text = "Добавить в дневник"

    def open_for_edit(self, entry_id: int, user_id: int, on_done=None):
        self._user_id = user_id
        self._edit_entry_id = entry_id
        self._on_done = on_done
        self._build_meal_buttons()

        def on_entry_loaded(entry):
            if not entry:
                self._show_error("Запись не найдена")
                self.go_back()
                return
            food = entry.food_item
            self.ids.name_field.text = food.name
            self.ids.cal_field.text = str(food.calories)
            self.ids.protein_field.text = str(food.protein)
            self.ids.fat_field.text = str(food.fat)
            self.ids.carbs_field.text = str(food.carbs)
            self.ids.grams_field.text = str(int(entry.grams))
            self._selected_food_id = food.id
            self._meal_key = entry.meal_type
            self._select_meal_btn(entry.meal_type)
            self.on_macro_changed()
            self.ids.screen_title.text = "Редактировать продукт"
            self.ids.submit_btn.children[0].text = "Сохранить изменения"
            self._check_submit()

        run_in_background(
            lambda: get_diary_entry(entry_id),
            on_entry_loaded,
            self._on_error
        )

    def submit(self):
        """Сохраняет запись в дневник (добавление или обновление)."""
        name = self.ids.name_field.text.strip()
        grams = self._float(self.ids.grams_field.text)
        cal = self._float(self.ids.cal_field.text)
        prot = self._float(self.ids.protein_field.text)
        fat = self._float(self.ids.fat_field.text)
        carbs = self._float(self.ids.carbs_field.text)

        if not self._validate_grams() or not self._validate_macros():
            self._show_error("Проверьте правильность введенных данных")
            return
        if not name or grams <= 0:
            self._show_error("Укажите название и количество граммов")
            return

        if self._edit_entry_id is not None:
            food_data = FoodItemCreate(
                name=name,
                calories=cal,
                protein=prot,
                fat=fat,
                carbs=carbs,
                is_custom=True
            )
            update_data = DiaryEntryUpdate(
                grams=grams,
                meal_type=self._meal_key,
                food_data=food_data
            )
            run_in_background(
                lambda: update_diary_entry(self._edit_entry_id, update_data),
                self._on_saved,
                self._on_error
            )
            return

        use_existing = False
        if self._selected_food_id is not None:
            existing = get_food_item(self._selected_food_id)
            if (existing and existing.name == name
                and abs(existing.calories - cal) < 0.01
                and abs(existing.protein - prot) < 0.01
                and abs(existing.fat - fat) < 0.01
                    and abs(existing.carbs - carbs) < 0.01):
                use_existing = True

        if use_existing:
            self._save_entry(self._selected_food_id, grams)
        else:
            self._create_food_and_save(name, cal, prot, fat, carbs, grams)

    def _build_meal_buttons(self):
        """Создаёт кнопки выбора приёма пищи (если ещё не созданы)."""
        box = self.ids.meal_selector
        if self._meal_btns:
            return
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
        """Выделяет выбранную кнопку приёма пищи."""
        self._meal_key = key
        for k, btn in self._meal_btns.items():
            is_active = (k == key)
            btn.theme_bg_color = "Custom"
            btn.md_bg_color = (0, 0, 0, 1) if is_active else (1, 1, 1, 0)
            text_widget = btn.children[0] if btn.children else None
            if text_widget:
                text_widget.text_color = (
                    1, 1, 1, 1) if is_active else (0, 0, 0, 1)
        self._check_submit()

    def on_search_text(self, text: str):
        """Обработчик ввода в поле поиска (с debounce)."""
        if self._search_event:
            self._search_event.cancel()
        q = text.strip()
        if len(q) < 2:
            self._hide_suggestions()
            return
        self._search_event = Clock.schedule_once(
            lambda dt: self._do_search(q), 0.3)

    def _do_search(self, query: str):
        """Выполняет поиск продуктов в фоне."""
        def task():
            return search_food(query, limit=7)
        run_in_background(task, self._on_search_result)

    def _on_search_result(self, items):
        """Отображает найденные продукты в выпадающем списке."""
        box = self.ids.suggestions_box
        card = self.ids.suggestions_card
        box.clear_widgets()
        if not items:
            self._hide_suggestions()
            return
        for food in items:
            item = MDListItem(ripple_effect=True, on_release=lambda x,
                              f=food: self._on_suggestion_selected(f))
            item.add_widget(MDListItemHeadlineText(text=food.name))
            supporting = f" {food.calories:.0f} ккал • Б:{food.protein:.0f}г Ж:{food.fat:.0f}г У:{food.carbs:.0f}г"
            item.add_widget(MDListItemSupportingText(text=supporting))
            if food.is_custom:
                item.add_widget(MDListItemTrailingIcon(icon="fire",
                                                       theme_icon_color="Custom",
                                                       icon_color=(0, 0, 1, 1)))
            else:
                item.add_widget(MDListItemTrailingIcon(icon="fire",
                                                       theme_icon_color="Custom",
                                                       icon_color=(1, 0, 0, 1)))
            box.add_widget(item)
            box.add_widget(MDDivider(size_hint_y=None, height=dp(1)))
        max_items = min(len(items), 5)
        target_h = max_items * dp(72) + len(items) * dp(1)
        target_h = min(target_h, dp(350))
        Animation.cancel_all(card)
        card.height = target_h
        card.opacity = 1.0

    def _hide_suggestions(self):
        """Скрывает выпадающий список подсказок."""
        card = self.ids.suggestions_card
        Animation.cancel_all(card)
        Animation(height=0, opacity=0, duration=0.15).start(card)

    def on_touch_down(self, touch):
        """Скрывает подсказки при касании вне области карточки."""
        card = self.ids.suggestions_card
        if card.opacity > 0 and card.height > 0:
            if not card.collide_point(*touch.pos):
                self._hide_suggestions()
        return super().on_touch_down(touch)

    def _on_suggestion_selected(self, food):
        """Выбрали продукт из подсказки — заполняем поля."""
        self.ids.search_field.text = food.name
        self.ids.name_field.text = food.name
        self.ids.cal_field.text = str(food.calories)
        self.ids.protein_field.text = str(food.protein)
        self.ids.fat_field.text = str(food.fat)
        self.ids.carbs_field.text = str(food.carbs)
        self._selected_food_id = food.id
        if not self.ids.grams_field.text:
            self.ids.grams_field.text = "100"
        self._hide_suggestions()
        self.on_macro_changed()

    def on_grams_changed(self, text: str):
        self._validate_grams()
        self.on_macro_changed()

    def on_macro_changed(self):
        """Пересчитывает итоговые КБЖУ для указанной порции и обновляет превью."""
        grams = self._float(self.ids.grams_field.text)
        cal100 = self._float(self.ids.cal_field.text)
        prot100 = self._float(self.ids.protein_field.text)
        fat100 = self._float(self.ids.fat_field.text)
        carbs100 = self._float(self.ids.carbs_field.text)

        card = self.ids.preview_card
        if grams > 0 and cal100 > 0:
            f = grams / 100
            self._update_preview(cal100 * f, prot100 * f,
                                 fat100 * f, carbs100 * f)
            Animation.cancel_all(card)
            card.height = dp(80)
            card.opacity = 1.0
        else:
            Animation.cancel_all(card)
            Animation(height=0, opacity=0, duration=0.15).start(card)

        self._validate_macros()
        self._check_submit()

    def _update_preview(self, cal, prot, fat, carbs):
        """Отображает итоговые КБЖУ для порции в виде цветных блоков."""
        row = self.ids.preview_row
        row.clear_widgets()
        defs = [
            ("ккал", f"{cal:.0f}", (0.18, 0.49, 0.31, 1)),
            ("белки", f"{prot:.1f} г", (0.36, 0.50, 0.83, 1)),
            ("жиры", f"{fat:.1f} г", (0.83, 0.53, 0.36, 1)),
            ("углев.", f"{carbs:.1f} г", (0.32, 0.66, 0.47, 1)),
        ]
        for label, value, color in defs:
            col = MDBoxLayout(orientation="vertical",
                              size_hint_x=1, spacing=dp(2))
            col.add_widget(MDLabel(
                text=value, font_style="Title", role="small",
                halign="center", valign="center", theme_text_color="Custom",
                text_color=color, size_hint_y=None, height=dp(28),
            ))
            col.add_widget(MDLabel(
                text=label, font_style="Label", role="small",
                halign="center", valign="center", theme_text_color="Custom",
                text_color=(0, 0, 0, 0.4), size_hint_y=None, height=dp(16),
            ))
            row.add_widget(col)

    def _validate_grams(self) -> bool:
        grams = self._float(self.ids.grams_field.text)
        field = self.ids.grams_field
        if not self.ids.grams_field.text.strip():
            field.helper_text, field.line_color_normal = "Укажите количество", (
                0.8, 0.2, 0.2, 0.5)
            return False
        if grams < self.GRAMS_MIN or grams > self.GRAMS_MAX:
            field.helper_text, field.line_color_normal = f"Допустимо: {self.GRAMS_MIN}-{self.GRAMS_MAX} г", (
                0.8, 0.2, 0.2, 0.5)
            return False
        field.helper_text, field.line_color_normal = f"Количество в граммах ({self.GRAMS_MIN}-{self.GRAMS_MAX})", (
            0, 0, 0, 0.3)
        return True

    def _validate_macros(self) -> bool:
        errors = []
        fields = [
            ("cal_field", self._float(self.ids.cal_field.text),
             self.CALORIES_MAX, "ккал"),
            ("protein_field", self._float(
                self.ids.protein_field.text), self.MACRO_MAX, "г"),
            ("fat_field", self._float(self.ids.fat_field.text),
             self.MACRO_MAX, "г"),
            ("carbs_field", self._float(self.ids.carbs_field.text),
             self.MACRO_MAX, "г"),
        ]
        for field_id, val, max_val, unit in fields:
            field = self.ids[field_id]
            if field.text.strip() and (val < 0 or val > max_val):
                field.helper_text, field.line_color_normal = f"0-{max_val} {unit}", (
                    0.8, 0.2, 0.2, 0.5)
                errors.append(field_id)
            else:
                field.helper_text, field.line_color_normal = f"0-{max_val} {unit}", (
                    0, 0, 0, 0.3)
        return len(errors) == 0

    def _check_submit(self):
        """Активирует кнопку «Добавить», если все поля валидны."""
        ok = bool(self.ids.name_field.text.strip()) and self._validate_grams(
        ) and self._validate_macros() and bool(self._meal_key)
        self.ids.submit_btn.disabled = not ok

    def _save_entry(self, food_id: int, grams: float):
        def task():
            return add_diary_entry(self._user_id, DiaryEntryCreate(food_item_id=food_id,
                                                                   grams=grams,
                                                                   meal_type=self._meal_key))
        run_in_background(task, self._on_saved, self._on_error)

    def _create_food_and_save(self, name, cal, prot, fat, carbs, grams):
        from services.food_service import add_food

        def task():
            food = add_food(FoodItemCreate(name=name, calories=cal,
                            protein=prot, fat=fat, carbs=carbs, is_custom=True))
            return add_diary_entry(self._user_id, DiaryEntryCreate(food_item_id=food.id,
                                                                   grams=grams,
                                                                   meal_type=self._meal_key))
        run_in_background(task, self._on_saved, self._on_error)

    def _on_saved(self, entry):
        self._clear_form()
        if self._on_done:
            self._on_done(entry)
        self.go_back()

    def _on_error(self, e):
        self._show_error(f"Ошибка: {e}")

    def go_back(self):
        if self.manager and self.manager.has_screen("home"):
            self.manager.current = "home"

    def _clear_form(self):
        for field_id in ("search_field",
                         "name_field",
                         "grams_field",
                         "cal_field",
                         "protein_field",
                         "fat_field",
                         "carbs_field"):
            self.ids[field_id].text = ""
            self.ids[field_id].line_color_normal = (0, 0, 0, 0.3)
        self._selected_food_id = None
        self._edit_entry_id = None
        self._hide_suggestions()
        card = self.ids.preview_card
        card.height, card.opacity = 0, 0
        self.ids.submit_btn.disabled = True
        self.ids.screen_title.text = "Добавить продукт"

    @staticmethod
    def _float(text: str) -> float:
        try:
            return max(0.0, float(text.strip().replace(",", ".")))
        except (ValueError, AttributeError):
            return 0.0

    def _show_error(self, msg: str):
        from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
        MDSnackbar(MDSnackbarText(text=msg), duration=2.5, pos_hint={
                   "center_x": 0.5, "center_y": 0.1}).open()
