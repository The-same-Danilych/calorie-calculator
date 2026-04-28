from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import NumericProperty
from datetime import datetime


class MainScreen(MDScreen):
    calories_consumed = NumericProperty(850)
    calories_goal = NumericProperty(2300)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Демо-данные
        self.demo_meals = [
            {
                "id": 1,
                "meal_type": "Завтрак",
                "eaten_at": datetime.now().replace(hour=8, minute=30),
                "notes": "Плотный завтрак",
                "total_calories": 350,
                "total_protein": 15.5,
                "total_fat": 12.3,
                "total_carbs": 45.2,
                "entries": [
                    {"food_name": "Овсяная каша",
                        "quantity_grams": 200, "calories": 180},
                    {"food_name": "Яйцо вареное",
                        "quantity_grams": 100, "calories": 155}
                ]
            },
            {
                "id": 2,
                "meal_type": "Обед",
                "eaten_at": datetime.now().replace(hour=13, minute=15),
                "notes": None,
                "total_calories": 420,
                "total_protein": 35.8,
                "total_fat": 14.2,
                "total_carbs": 48.5,
                "entries": [
                    {"food_name": "Куриная грудка",
                        "quantity_grams": 150, "calories": 248},
                    {"food_name": "Рис отварной",
                        "quantity_grams": 150, "calories": 172}
                ]
            },
            {
                "id": 3,
                "meal_type": "Ужин",
                "eaten_at": datetime.now().replace(hour=16, minute=0),
                "notes": "Быстрый перекус",
                "total_calories": 80,
                "total_protein": 4.2,
                "total_fat": 2.1,
                "total_carbs": 18.3,
                "entries": [
                    {"food_name": "Яблоко", "quantity_grams": 150, "calories": 78}
                ]
            }
        ]
        self.build_ui()

    def build_ui(self):
        # Основной контейнер
        main_layout = MDBoxLayout(orientation='vertical')

        # Верхняя панель (без кнопки меню)
        toolbar = MDTopAppBar(
            title="Счётчик калорий",
            right_action_items=[
                ["account-circle", lambda x: self.show_profile()]],
            elevation=10
        )

        # Контент с прокруткой
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(15), dp(10), dp(15), dp(10)],
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        # Карточка с калориями
        calories_card = self.create_calories_card()
        content.add_widget(calories_card)

        # Сегодняшние приемы пищи
        meals_header = MDLabel(
            text="Сегодня",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(meals_header)

        # Список приемов пищи
        for meal in self.demo_meals:
            meal_card = self.create_meal_card(meal)
            content.add_widget(meal_card)

        main_layout.add_widget(toolbar)
        main_layout.add_widget(content)

        # Кнопка добавления внизу
        add_button = MDRaisedButton(
            text="+ Добавить приём пищи",
            size_hint=(1, None),
            height=dp(56),
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.7, 0.2, 1),
            on_release=self.add_meal
        )

        self.add_widget(main_layout)
        self.add_widget(add_button)

    def create_calories_card(self):
        """Создание карточки с информацией о калориях"""
        card = MDCard(
            size_hint=(1, None),
            height=dp(180),
            padding=dp(20),
            elevation=10,
            radius=[20, 20, 20, 20]
        )

        card_content = MDBoxLayout(orientation='vertical', spacing=dp(15))

        # Заголовок
        title = MDLabel(
            text="Калории сегодня",
            font_style="H6",
            halign="center"
        )

        # Прогресс
        self.calories_label = MDLabel(
            text=f"{self.calories_consumed} / {self.calories_goal} ккал",
            font_style="H4",
            halign="center",
            bold=True
        )

        # Процент
        percentage = (self.calories_consumed / self.calories_goal) * 100
        self.progress_label = MDLabel(
            text=f"{percentage:.1f}% от дневной нормы",
            font_style="H6",
            halign="center",
            theme_text_color="Secondary"
        )

        # Прогресс-бар
        progress_text = self.create_progress_bar(percentage)
        self.progress_bar = MDLabel(
            text=progress_text,
            font_style="H6",
            halign="center"
        )

        card_content.add_widget(title)
        card_content.add_widget(self.calories_label)
        card_content.add_widget(self.progress_label)
        card_content.add_widget(self.progress_bar)

        card.add_widget(card_content)
        return card

    def create_progress_bar(self, percentage, width=25):
        """Создание текстового прогресс-бара"""
        filled = int((percentage / 100) * width)
        empty = width - filled
        bar = "[" + "█" * filled + "░" * empty + "]"
        return bar

    def create_meal_card(self, meal):
        """Создание карточки приёма пищи"""
        card = MDCard(
            size_hint=(1, None),
            height=dp(90),
            padding=dp(15),
            elevation=3,
            radius=[15, 15, 15, 15]
        )

        card_content = MDBoxLayout(orientation='vertical', spacing=dp(5))

        # Верхняя строка: тип приема и время
        top_row = MDBoxLayout(size_hint_y=None, height=dp(30))

        meal_type_label = MDLabel(
            text=meal.get('meal_type', 'Приём пищи'),
            font_style="Subtitle1",
            bold=True
        )

        time_label = MDLabel(
            text=meal.get('eaten_at', datetime.now()).strftime("%H:%M"),
            font_style="Caption",
            theme_text_color="Secondary",
            halign="right"
        )

        top_row.add_widget(meal_type_label)
        top_row.add_widget(time_label)

        # Нижняя строка: список продуктов и калории
        bottom_row = MDBoxLayout(size_hint_y=None, height=dp(20))

        # Список продуктов
        foods_text = ", ".join([entry.get('food_name', '')
                               for entry in meal.get('entries', [])])
        foods_label = MDLabel(
            text=foods_text[:40] +
            "..." if len(foods_text) > 40 else foods_text,
            font_style="Caption",
            theme_text_color="Secondary"
        )

        # Калории
        calories_label = MDLabel(
            text=f"{meal.get('total_calories', 0)} ккал",
            font_style="Subtitle1",
            bold=True,
            halign="right",
            size_hint_x=None,
            width=dp(80)
        )

        bottom_row.add_widget(foods_label)
        bottom_row.add_widget(calories_label)

        card_content.add_widget(top_row)
        card_content.add_widget(bottom_row)

        card.add_widget(card_content)
        return card

    def add_meal(self, instance):
        """Добавление приема пищи (заглушка)"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton

        dialog = MDDialog(
            title="Добавить приём пищи",
            text="Здесь будет форма добавления приёма пищи",
            buttons=[
                MDFlatButton(
                    text="ОТМЕНА",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="ДОБАВИТЬ",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()

    def show_profile(self):
        """Показать профиль (заглушка)"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton

        dialog = MDDialog(
            title="Профиль",
            text="Здесь будет профиль пользователя",
            buttons=[
                MDFlatButton(
                    text="ЗАКРЫТЬ",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()
