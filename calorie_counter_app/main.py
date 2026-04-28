from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.utils import platform

# Настройка размера окна
Window.size = (400, 700)


class CalorieCounterApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        self.title = "Счётчик калорий"

        from main_screen import MainScreen

        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))

        return sm


if __name__ == '__main__':
    CalorieCounterApp().run()
