"""
Экран-заставка: инициализация БД,
начальное заполнение, проверка пользователя.
Добавлено приветствие с именем пользователя (если он уже зарегистрирован).
"""

from kivy.lang import Builder
from kivy.animation import Animation
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
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
        spacing: dp(20)
        size_hint: None, None
        size: dp(200), dp(320)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        FitImage:
            id: app_icon
            source: root.get_icon_path()
            size_hint: None, None
            size: dp(120), dp(120)
            pos_hint: {'center_x': 0.5}
            fit_mode: "contain"
            radius: "42dp", "42dp", "42dp", "42dp"
        MDLabel:
            id: greeting_label
            text: ""
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            font_style: "Body"
            role: "large"
            size_hint_y: None
            height: dp(48)
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
        """Запускает фоновую инициализацию БД и анимацию."""
        run_in_background(
            self._init_db_and_seed,
            on_success=self._on_db_ready,
            on_error=self._on_db_error
        )
        self.ids.loader.start()
        Clock.schedule_once(self._on_min_time_passed, 5)
        self._start_animation()

    def _start_animation(self):
        """Пульсирующая анимация иконки."""
        icon = self.ids.app_icon
        Animation.cancel_all(icon)
        anim = Animation(opacity=0.6, duration=0.8, t='out_quad') + \
            Animation(opacity=1.0, duration=0.8, t='in_quad')
        anim.repeat = True
        anim.start(icon)

    def _init_db_and_seed(self):
        """
        Создаёт таблицы и загружает начальные продукты
        (выполняется в фоне).
        """
        init_db()
        seed_initial_foods()
        return True

    def _on_db_ready(self, result):
        """Вызывается после успешной инициализации БД."""
        self._db_ready = True
        get_user_async(self._after_user_check)

    def _after_user_check(self, user):
        """
        Определяет, есть ли уже пользователь в БД,
        и устанавливает приветствие.
        """
        self._set_greeting(user)
        self._pending_transition = "home" if user else "onboarding"
        self._try_transition()

    def _set_greeting(self, user):
        """Устанавливает текст приветствия на экране заставки."""
        label = self.ids.get("greeting_label")
        if label:
            if user and user.name:
                label.text = f"Как вы себя чувствуете, {user.name}?"
            else:
                label.text = "Как вы себя чувствуете?"

    def _on_min_time_passed(self, dt):
        """Минимальное время показа заставки истекло."""
        self._min_time_passed = True
        self._try_transition()

    def _try_transition(self):
        """Переход на следующий экран, если выполнены оба условия."""
        if (self._db_ready and self._min_time_passed
                and self._pending_transition):
            Clock.schedule_once(lambda dt: self._do_transition(
                self._pending_transition), 0.1)

    def _do_transition(self, target_screen):
        """Выполняет смену экрана."""
        if self.manager and self.manager.has_screen(target_screen):
            self.manager.current = target_screen

    def _on_db_error(self, error):
        """Обработка ошибки инициализации БД."""
        print(f"Ошибка инициализации БД: {error}")
        from kivymd.uix.dialog import MDDialog
        MDDialog(
            title="Ошибка",
            text="Не удалось загрузить данные приложения." \
            "Попробуйте переустановить.",
        ).open()

    def get_icon_path(self) -> str:
        """Путь к иконке приложения."""
        return image("boot_picture.png")