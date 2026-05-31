# ui/splash_screen.py
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.loadingindicator import MDLoadingIndicator
from kivymd.uix.fitimage import FitImage
from config import image

from database.engine import init_db
from database.seed import seed_initial_foods
from services.user_service import get_user_async
from utils.async_db import run_in_background

KV = '''
<SplashScreen>:
    md_bg_color: 0.2, 0.6, 0.2, 1
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(30)
        size_hint: None, None
        size: dp(200), dp(250)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        FitImage:
            id: app_icon
            source: root.get_icon_path()
            size_hint: None, None
            size: dp(120), dp(120)
            pos_hint: {'center_x': 0.5}
            fit_mode: "contain"
            radius: "42dp", "42dp", "42dp", "42dp"
        MDLoadingIndicator:
            id: loader
            shape_size: dp(48)
            active_indicator_color: 1, 1, 1, 1
            container_color: 0, 0, 0, 0
            size_hint: None, None
            size: dp(48), dp(48)
            pos_hint: {'center_x': 0.5}
            active: True
'''

Builder.load_string(KV)


class SplashScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._db_ready = False
        self._min_time_passed = False
        self._pending_transition = None

    def on_enter(self):
        run_in_background(
            self._init_db_and_seed,
            on_success=self._on_db_ready,
            on_error=self._on_db_error
        )
        self.ids.loader.start()
        Clock.schedule_once(self._on_min_time_passed, 5)
        self._start_animation()

    def _start_animation(self):
        icon = self.ids.app_icon
        Animation.cancel_all(icon)
        # Пульсация прозрачности (безопасно, opacity есть у всех виджетов)
        anim = Animation(opacity=0.6, duration=0.8, t='out_quad') + \
               Animation(opacity=1.0, duration=0.8, t='in_quad')
        anim.repeat = True
        anim.start(icon)

    def _init_db_and_seed(self):
        init_db()
        seed_initial_foods()
        return True

    def _on_db_ready(self, result):
        self._db_ready = True
        get_user_async(self._after_user_check)

    def _after_user_check(self, user):
        self._pending_transition = "home" if user else "onboarding"
        self._try_transition()

    def _on_min_time_passed(self, dt):
        self._min_time_passed = True
        self._try_transition()

    def _try_transition(self):
        if self._db_ready and self._min_time_passed and self._pending_transition:
            Clock.schedule_once(lambda dt: self._do_transition(self._pending_transition), 0.1)

    def _do_transition(self, target_screen):
        if self.manager and self.manager.has_screen(target_screen):
            self.manager.current = target_screen

    def _on_db_error(self, error):
        print(f"Ошибка инициализации БД: {error}")
        from kivymd.uix.dialog import MDDialog
        MDDialog(
            title="Ошибка",
            text="Не удалось загрузить данные приложения. Попробуйте переустановить.",
        ).open()

    def get_icon_path(self) -> str:
        return image("boot_picture.png")  # замените на имя вашего файла