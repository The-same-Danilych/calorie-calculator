# ui/home/home_screen.py
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Ellipse, Line
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout

from services.diary_service import get_day_summary
from services.user_service import get_user_async
from utils.async_db import run_in_background
from ui.main_screen.widgets.macro_bar import MacroBar
from ui.main_screen.widgets.meal_section import MealSection

KV_HOME = """
#:import dp kivy.metrics.dp
#:import datetime datetime.datetime

<CalorieRing>:
    size_hint: None, None
    size: dp(120), dp(120)

<HomeScreen>:

    MDBoxLayout:
        orientation: "vertical"
        size_hint: 1, 1

        # ── AppBar ──────────────────────────────────────────────────
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: dp(56)
            padding: [dp(8), dp(4), dp(8), dp(4)]
            spacing: dp(4)
            md_bg_color: 1, 1, 1, 1

            MDIconButton:
                icon: "menu"
                size_hint: None, None
                size: dp(48), dp(48)
                pos_hint: {"center_y": 0.5}
                theme_icon_color: "Custom"
                icon_color: 0, 0, 0, 1
                on_release: root.open_drawer()

            MDLabel:
                text: "Дневник"
                font_style: "Title"
                role: "large"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                valign: "center"
                size_hint_x: 1

            MDIconButton:
                id: theme_btn
                icon: "weather-sunny"
                size_hint: None, None
                size: dp(48), dp(48)
                pos_hint: {"center_y": 0.5}
                theme_icon_color: "Custom"
                icon_color: 0, 0, 0, 1
                on_release: root.toggle_theme()

        MDDivider:
            size_hint_y: None
            height: dp(1)

        # ── Прокручиваемое тело ─────────────────────────────────────
        MDScrollView:
            id: scroll
            do_scroll_x: False
            bar_width: 0

            MDBoxLayout:
                id: body
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(16), dp(16), dp(16), dp(96)]
                spacing: dp(12)

                # ── Карточка: кольцо + остаток ──────────────────────
                MDCard:
                    id: calorie_card
                    style: "elevated"
                    elevation: 1
                    radius: [dp(16)]
                    size_hint_y: None
                    height: dp(120)
                    padding: [dp(16), dp(12), dp(16), dp(12)]
                    md_bg_color: 1, 1, 1, 1

                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: dp(20)

                        CalorieRing:
                            id: calorie_ring

                        MDBoxLayout:
                            orientation: "vertical"
                            spacing: dp(4)
                            pos_hint: {"center_y": 0.5}

                            MDLabel:
                                id: goal_label
                                text: "Цель: — ккал"
                                font_style: "Label"
                                role: "large"
                                theme_text_color: "Custom"
                                text_color: 0, 0, 0, 0.5
                                size_hint_y: None
                                height: dp(18)

                            MDLabel:
                                id: remaining_label
                                text: "— ккал осталось"
                                font_style: "Title"
                                role: "small"
                                theme_text_color: "Custom"
                                text_color: 0.18, 0.49, 0.31, 1
                                size_hint_y: None
                                height: dp(24)

                            MDLabel:
                                id: date_label
                                text: ""
                                font_style: "Label"
                                role: "medium"
                                theme_text_color: "Custom"
                                text_color: 0, 0, 0, 0.35
                                size_hint_y: None
                                height: dp(16)

                # ── Карточка: шкалы БЖУ ─────────────────────────────
                MDCard:
                    id: macro_card
                    style: "elevated"
                    elevation: 1
                    radius: [dp(16)]
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(16), dp(12), dp(16), dp(12)]
                    md_bg_color: 1, 1, 1, 1

                    MDBoxLayout:
                        id: macro_box
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height

                # ── Заголовок «Приёмы пищи» ─────────────────────────
                MDLabel:
                    text: "Приёмы пищи"
                    font_style: "Title"
                    role: "medium"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 0.8
                    size_hint_y: None
                    height: dp(32)
                    padding_x: dp(4)

                # ── Секции приёмов (добавляются динамически) ─────────
                MDBoxLayout:
                    id: meals_box
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(10)

    # ── FAB ─────────────────────────────────────────────────────────
    MDFloatLayout:
        size_hint: None, None
        size: 0, 0
        pos_hint: {"right": 1, "y": 0}

        MDFabButton:
            id: fab
            icon: "plus"
            style: "standard"
            size_hint: None, None
            size: dp(56), dp(56)
            pos_hint: {"right": 0.93, "y": 0.04}
            theme_bg_color: "Custom"
            md_bg_color: 0, 0, 0, 1
            theme_icon_color: "Custom"
            icon_color: 1, 1, 1, 1
            on_release: root.open_add_sheet()

    # ── BottomSheet (оверлей) ────────────────────────────────────────
    MDBoxLayout:
        id: sheet_overlay
        opacity: 0
        size_hint: 1, 1
        md_bg_color: 0, 0, 0, 0.45
        on_touch_down: root.close_sheet_on_bg(*args)

        MDBoxLayout:
            id: sheet
            orientation: "vertical"
            size_hint: 1, None
            height: 0
            pos_hint: {"bottom": 1}
            radius: [dp(20), dp(20), 0, 0]
            md_bg_color: 1, 1, 1, 1
            padding: [0, dp(8), 0, dp(24)]

            # Ручка
            MDBoxLayout:
                size_hint_y: None
                height: dp(24)
                MDBoxLayout:
                    size_hint: None, None
                    size: dp(36), dp(4)
                    radius: [dp(2)]
                    md_bg_color: 0, 0, 0, 0.15
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}

            MDLabel:
                text: "Добавить продукт"
                font_style: "Label"
                role: "large"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 0.4
                halign: "left"
                size_hint_y: None
                height: dp(32)
                padding_x: dp(20)

            # Опция: вручную
            MDBoxLayout:
                id: opt_manual
                orientation: "horizontal"
                size_hint_y: None
                height: dp(64)
                padding: [dp(20), dp(8), dp(20), dp(8)]
                spacing: dp(16)
                on_touch_down: root.sheet_option_touch(self, args[0], "manual")

                MDBoxLayout:
                    size_hint: None, None
                    size: dp(44), dp(44)
                    radius: [dp(13)]
                    md_bg_color: 0.91, 0.95, 0.87, 1
                    pos_hint: {"center_y": 0.5}

                    MDIconButton:
                        icon: "pencil-outline"
                        size_hint: None, None
                        size: dp(44), dp(44)
                        theme_icon_color: "Custom"
                        icon_color: 0.23, 0.43, 0.07, 1
                        on_release: root.go_to_add("manual")

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_x: 1
                    spacing: dp(2)
                    pos_hint: {"center_y": 0.5}

                    MDLabel:
                        text: "Ввести вручную"
                        font_style: "Body"
                        role: "large"
                        theme_text_color: "Custom"
                        text_color: 0, 0, 0, 0.88
                        size_hint_y: None
                        height: dp(22)

                    MDLabel:
                        text: "Название, граммы, КБЖУ или поиск по базе"
                        font_style: "Label"
                        role: "medium"
                        theme_text_color: "Custom"
                        text_color: 0, 0, 0, 0.4
                        size_hint_y: None
                        height: dp(18)

                MDIconButton:
                    icon: "chevron-right"
                    size_hint: None, None
                    size: dp(32), dp(32)
                    pos_hint: {"center_y": 0.5}
                    theme_icon_color: "Custom"
                    icon_color: 0, 0, 0, 0.25
                    on_release: root.go_to_add("manual")

            MDDivider:
                size_hint_y: None
                height: dp(1)
                padding: [dp(20), 0, dp(20), 0]

            # Опция: штрихкод
            MDBoxLayout:
                id: opt_barcode
                orientation: "horizontal"
                size_hint_y: None
                height: dp(64)
                padding: [dp(20), dp(8), dp(20), dp(8)]
                spacing: dp(16)
                on_touch_down: root.sheet_option_touch(self, args[0], "barcode")

                MDBoxLayout:
                    size_hint: None, None
                    size: dp(44), dp(44)
                    radius: [dp(13)]
                    md_bg_color: 0.90, 0.94, 0.98, 1
                    pos_hint: {"center_y": 0.5}

                    MDIconButton:
                        icon: "barcode-scan"
                        size_hint: None, None
                        size: dp(44), dp(44)
                        theme_icon_color: "Custom"
                        icon_color: 0.09, 0.37, 0.64, 1
                        on_release: root.go_to_add("barcode")

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_x: 1
                    spacing: dp(2)
                    pos_hint: {"center_y": 0.5}

                    MDLabel:
                        text: "Сканировать штрихкод"
                        font_style: "Body"
                        role: "large"
                        theme_text_color: "Custom"
                        text_color: 0, 0, 0, 0.88
                        size_hint_y: None
                        height: dp(22)

                    MDLabel:
                        text: "Автоматически заполнит из базы"
                        font_style: "Label"
                        role: "medium"
                        theme_text_color: "Custom"
                        text_color: 0, 0, 0, 0.4
                        size_hint_y: None
                        height: dp(18)

                MDIconButton:
                    icon: "chevron-right"
                    size_hint: None, None
                    size: dp(32), dp(32)
                    pos_hint: {"center_y": 0.5}
                    theme_icon_color: "Custom"
                    icon_color: 0, 0, 0, 0.25
                    on_release: root.go_to_add("barcode")
"""

Builder.load_string(KV_HOME)

# ──────────────────────────────────────────────────────────────────────── #
MEAL_META = {
    "breakfast": ("Завтрак",  "🌅", [1.0,  0.95, 0.88, 1]),
    "lunch":     ("Обед",     "☀️", [0.91, 0.97, 0.91, 1]),
    "dinner":    ("Ужин",     "🌙", [0.93, 0.90, 0.98, 1]),
    "snack":     ("Перекус",  "🍎", [0.99, 0.91, 0.94, 1]),
}


# ── Виджет кольца калорий ─────────────────────────────────────────────── #
class CalorieRing(MDBoxLayout):
    """
    Рисует круговую диаграмму прогресса поверх центральной подписи.
    eaten  — сколько съедено (ккал)
    goal   — дневная цель (ккал)
    """
    eaten = NumericProperty(0)
    goal  = NumericProperty(2000)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(eaten=self._redraw, goal=self._redraw, size=self._redraw)
        Clock.schedule_once(self._build_labels, 0)

    def _build_labels(self, *_):
        self._num_lbl = _make_label("0", "Display", "small", (0, 0, 0, 1))
        self._sub_lbl = _make_label("ккал", "Label", "medium", (0, 0, 0, 0.45))
        self.add_widget(self._num_lbl)
        self.add_widget(self._sub_lbl)
        self._redraw()

    def _redraw(self, *_):
        if not hasattr(self, "_num_lbl"):
            return
        self._num_lbl.text = f"{self.eaten:.0f}"
        self.canvas.before.clear()

        cx, cy = self.center
        r_outer = min(self.width, self.height) / 2 - dp(6)
        stroke  = dp(8)
        r_inner = r_outer - stroke

        with self.canvas.before:
            # Фоновая дуга (серая)
            Color(0.88, 0.88, 0.88, 1)
            Line(
                circle=(cx, cy, r_outer - stroke / 2, 0, 360),
                width=stroke,
                cap="none",
            )
            # Прогресс (зелёный)
            ratio = min(self.eaten / max(self.goal, 1), 1.0)
            if ratio > 0:
                Color(0.18, 0.49, 0.31, 1)
                Line(
                    circle=(cx, cy, r_outer - stroke / 2, 90, 90 - ratio * 360),
                    width=stroke,
                    cap="round",
                )


# ── Вспомогательная фабрика Label ────────────────────────────────────── #
def _make_label(text, style, role, color):
    from kivymd.uix.label import MDLabel
    return MDLabel(
        text=text,
        font_style=style,
        role=role,
        halign="center",
        valign="center",
        theme_text_color="Custom",
        text_color=color,
    )


# ── Главный экран ─────────────────────────────────────────────────────── #
class HomeScreen(MDScreen):

    _is_dark   = False
    _user      = None
    _user_id   = 1
    _sheet_open = False
    _active_meal_key = "lunch"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (0.96, 0.96, 0.94, 1)

    # ------------------------------------------------------------------ #
    def on_enter(self):
        self._set_today_label()
        self._load_data()

    # ── Загрузка данных ───────────────────────────────────────────── #
    def _load_data(self):
        get_user_async(self._on_user_loaded)

    def _on_user_loaded(self, user):
        if not user:
            return
        self._user    = user
        self._user_id = user.id
        self._build_macro_bars(user)
        self._update_goal_label(user.calorie_goal)
        self._load_diary()

    def _load_diary(self):
        uid = self._user_id

        def task():
            return get_day_summary(uid)

        run_in_background(task, self._on_diary_loaded)

    def _on_diary_loaded(self, summary: dict):
        meals  = summary.get("meals", {})
        totals = summary.get("totals", {})

        # Обновляем кольцо
        eaten = totals.get("calories", 0)
        goal  = self._user.calorie_goal if self._user else 2000
        self.ids.calorie_ring.eaten = eaten
        self.ids.calorie_ring.goal  = goal
        remaining = max(goal - eaten, 0)
        self.ids.remaining_label.text = f"{remaining:.0f} ккал осталось"

        # Обновляем шкалы БЖУ
        if self._user and hasattr(self, "_macro_bars"):
            mb = self._macro_bars
            mb["protein"].eaten = totals.get("protein", 0)
            mb["fat"].eaten     = totals.get("fat",     0)
            mb["carbs"].eaten   = totals.get("carbs",   0)

        # Обновляем секции приёмов
        for key, section in self._meal_sections.items():
            section.set_entries(meals.get(key, []))

    # ── Строим шкалы БЖУ ──────────────────────────────────────────── #
    def _build_macro_bars(self, user):
        box = self.ids.macro_box
        box.clear_widgets()

        defs = [
            ("protein", "Белки",    user.protein_goal, [0.36, 0.50, 0.83, 1]),
            ("fat",     "Жиры",     user.fat_goal,     [0.83, 0.53, 0.36, 1]),
            ("carbs",   "Углеводы", user.carb_goal,    [0.32, 0.66, 0.47, 1]),
        ]
        self._macro_bars = {}
        for key, label, goal, color in defs:
            bar = MacroBar(label=label, bar_color=color, goal=goal, eaten=0)
            self._macro_bars[key] = bar
            box.add_widget(bar)

    # ── Строим секции приёмов ─────────────────────────────────────── #
    def on_kv_post(self, base_widget):
        box = self.ids.meals_box
        self._meal_sections = {}

        for key, (title, emoji, bg) in MEAL_META.items():
            section = MealSection(
                meal_key=key,
                meal_title=title,
                icon_emoji=emoji,
                icon_bg_color=bg,
                on_add_callback=self._on_meal_add,
                on_delete_callback=self._on_entry_delete,
            )
            self._meal_sections[key] = section
            box.add_widget(section)

    # ── Вспомогательные ───────────────────────────────────────────── #
    def _set_today_label(self):
        from datetime import date
        import locale
        try:
            locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
        except locale.Error:
            pass
        today = date.today()
        # В Windows %d выводит день с ведущим нулём (01, 02...), уберём его вручную
        day = today.strftime("%d").lstrip("0") or "0"  # если вдруг "00" – оставим "0"
        month = today.strftime("%B").lower()
        self.ids.date_label.text = f"сегодня, {day} {month}"

    def _update_goal_label(self, goal: float):
        self.ids.goal_label.text = f"Цель: {goal:.0f} ккал"

    # ── FAB и BottomSheet ─────────────────────────────────────────── #
    def open_add_sheet(self, meal_key: str = "lunch"):
        self._active_meal_key = meal_key
        self._open_sheet()

    def _open_sheet(self):
        from kivy.animation import Animation
        overlay = self.ids.sheet_overlay
        sheet   = self.ids.sheet
        overlay.opacity = 0
        sheet.height    = 0
        self._sheet_open = True
        Animation(opacity=1, duration=0.2).start(overlay)
        Animation(height=dp(260), duration=0.28, t="out_cubic").start(sheet)

    def _close_sheet(self):
        from kivy.animation import Animation
        self._sheet_open = False
        overlay = self.ids.sheet_overlay
        sheet   = self.ids.sheet
        Animation(opacity=0, duration=0.18).start(overlay)
        Animation(height=0, duration=0.2, t="in_cubic").start(sheet)

    def close_sheet_on_bg(self, widget, touch):
        if not self._sheet_open:
            return
        # Закрываем только по тапу на затемнение, не на сам sheet
        if self.ids.sheet.collide_point(*touch.pos):
            return
        if widget.collide_point(*touch.pos):
            self._close_sheet()

    def sheet_option_touch(self, widget, touch, mode: str):
        if widget.collide_point(*touch.pos):
            self.go_to_add(mode)

    def go_to_add(self, mode: str):
        self._close_sheet()
        Clock.schedule_once(lambda dt: self._navigate_to_add(mode), 0.2)

    def _navigate_to_add(self, mode: str):
        if not self.manager or not self.manager.has_screen("add_food"):
            return
        screen = self.manager.get_screen("add_food")
        screen.open_for(
            meal_key=self._active_meal_key,
            user_id=self._user_id,
            on_done=self._on_food_added,
        )
        if mode == "barcode":
            # Запускаем сканер и потом вызываем screen.fill_from_barcode()
            self._open_barcode_scanner(screen)
        self.manager.current = "add_food"

    def _open_barcode_scanner(self, add_screen):
        """
        Заглушка под камеру/штрихкод-сканер.
        Реализуй через zbarcam / pyzbar / kivy Camera + ZBarSymbol.
        После успешного сканирования вызови:
            food = get_food_by_barcode(scanned_code)
            if food:
                add_screen.fill_from_barcode(food)
        """
        from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
        MDSnackbar(
            MDSnackbarText(text="Сканер штрихкода — в разработке"),
            duration=2,
            pos_hint={"center_x": 0.5, "center_y": 0.1},
        ).open()

    def _on_meal_add(self, meal_key: str):
        self._active_meal_key = meal_key
        self._open_sheet()

    def _on_entry_delete(self, entry_id: int):
        from services.diary_service import delete_entry

        def task():
            return delete_entry(entry_id)

        run_in_background(task, lambda _: self._load_diary())

    def _on_food_added(self, entry):
        """Вызывается после успешного добавления продукта."""
        self._load_diary()

    # ── Тема ──────────────────────────────────────────────────────── #
    def toggle_theme(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        self._is_dark = not self._is_dark
        app.theme_cls.theme_style = "Dark" if self._is_dark else "Light"
        # обновляем фон экрана
        self.md_bg_color = app.theme_cls.backgroundColor
        # обновляем фон карточек
        self.ids.calorie_card.md_bg_color = app.theme_cls.backgroundColor
        self.ids.macro_card.md_bg_color = app.theme_cls.backgroundColor
        self.ids.sheet.md_bg_color = app.theme_cls.backgroundColor

    # ── Боковое меню (заглушка) ───────────────────────────────────── #
    def open_drawer(self):
        """
        Подключи MDNavigationDrawer в main.py и вызывай его здесь.
        Например: app.root.ids.nav_drawer.set_state("open")
        """
        from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
        MDSnackbar(
            MDSnackbarText(text="Боковое меню — в разработке"),
            duration=1.5,
            pos_hint={"center_x": 0.5, "center_y": 0.1},
        ).open()