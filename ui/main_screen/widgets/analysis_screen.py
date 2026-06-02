"""Экран статистики: столбчатая диаграмма калорий за последние 7 дней."""

from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from services.diary_service import get_week_calories
from services.user_service import get_user_async
from utils.async_db import run_in_background
from datetime import datetime

KV_ANALYSIS = """
<AnalysisScreen>:
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: (1, 1, 1, 1)

        MDTopAppBar:
            title: "Статистика за неделю"
            elevation: 0
            md_bg_color: (1, 1, 1, 1)
            left_action_items: [["arrow-left", lambda x: root.go_back()]]

        MDScrollView:
            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(16)
                padding: dp(16)
                size_hint_y: None
                height: self.minimum_height

                MDLabel:
                    id: info_label
                    text: "Загрузка данных..."
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: (0, 0, 0, 0.7)

                MDCard:
                    id: chart_card
                    style: "elevated"
                    elevation: 2
                    radius: [dp(16)]
                    padding: dp(16)
                    size_hint_y: None
                    height: dp(300)
                    md_bg_color: (1, 1, 1, 1)

                    MDBoxLayout:
                        id: chart_container
                        orientation: "horizontal"
                        spacing: dp(8)
                        size_hint_y: None
                        height: dp(250)
                        padding: dp(8)

                MDButton:
                    style: "filled"
                    size_hint_x: 0.9
                    size_hint_y: None
                    height: dp(52)
                    pos_hint: {"center_x": 0.5}
                    theme_bg_color: "Custom"
                    md_bg_color: (0, 0, 0, 1)
                    on_release: root.go_back()
                    MDButtonText:
                        text: "Выход"
                        theme_text_color: "Custom"
                        text_color: (1, 1, 1, 1)
"""

Builder.load_string(KV_ANALYSIS)


class AnalysisScreen(MDScreen):
    """Экран с графиком калорийности за последнюю неделю."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None
        self.week_data = []

    def on_enter(self):
        get_user_async(self.on_user_loaded)

    def on_user_loaded(self, user):
        self.user = user
        if user:
            run_in_background(
                lambda: get_week_calories(user.id),
                on_success=self.on_data_loaded,
                on_error=self.on_error
            )
        else:
            self.go_back()

    def on_data_loaded(self, data):
        self.week_data = data
        self.build_chart()

    def build_chart(self):
        """Строит столбчатую диаграмму."""
        container = self.ids.chart_container
        container.clear_widgets()
        if not self.week_data:
            container.add_widget(
                MDLabel(text="Нет данных за последние 7 дней", halign="center"))
            return

        self.week_data.sort(key=lambda x: x["date"] if isinstance(
            x["date"], str) else x["date"])
        max_cal = max((d["calories"] for d in self.week_data), default=0)
        max_cal = max(max_cal, 1)

        for item in self.week_data:
            if isinstance(item["date"], str):
                date_obj = datetime.strptime(item["date"], "%Y-%m-%d").date()
            else:
                date_obj = item["date"]
            day_str = date_obj.strftime("%d.%m")
            cal = item["calories"]
            height_norm = min((cal / max_cal) * 200, 200)

            column = MDBoxLayout(orientation="vertical", size_hint_x=None, width=dp(
                50), spacing=dp(4), pos_hint={"center_x": 0.5})
            bar = MDCard(
                size_hint_x=None, width=dp(36), size_hint_y=None, height=dp(height_norm),
                md_bg_color=(0.2, 0.6, 0.8, 1), radius=[dp(4)],
                elevation=0,
                ripple_behavior=False,
                pos_hint={"center_x": 0.5}
            )
            label = MDLabel(text=f"{day_str}\n{int(cal)} ккал", halign="center",
                            size_hint_y=None,
                            height=dp(40),
                            theme_text_color="Secondary")
            column.add_widget(bar)
            column.add_widget(label)
            container.add_widget(column)

    def on_error(self, error):
        MDSnackbar(MDSnackbarText(text=f"Ошибка загрузки статистики: {error}"),
                   duration=2).open()
        self.go_back()

    def go_back(self):
        if self.manager and self.manager.has_screen("home"):
            self.manager.current = "home"
