"""Компонент выбора возраста: всплывающий поппер с прокручиваемым списком."""

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from ui.onboarding.screens.progress_bar import ProgressBarHeader

KV_AGE_PICKER = '''
<SelectableRecycleButton>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(52)
    md_bg_color: (1, 1, 1, 1)

<AgeRecycleView>:
    viewclass: 'SelectableRecycleButton'
    RecycleBoxLayout:
        default_size: None, dp(52)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        spacing: 0
'''

Builder.load_string(KV_AGE_PICKER)


class SelectableRecycleButton(RecycleDataViewBehavior, MDBoxLayout):
    """Отдельный элемент списка возрастов (кнопка)."""
    text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button = MDButton(
            MDButtonText(
                text=self.text,
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1)
            ),
            style="text",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            on_release=self.on_select
        )
        self.add_widget(self.button)

    def on_select(self, *args):
        """
        При нажатии на кнопку передаём
        выбранное значение родительскому RV.
        """
        parent = self.parent
        while parent:
            if hasattr(parent, 'select_item'):
                parent.select_item(self.text)
                break
            parent = getattr(parent, 'parent', None)

    def refresh_view_attrs(self, rv, index, data):
        """Обновляет текст кнопки при переиспользовании представления."""
        self.text = data['text']
        if self.button.children:
            self.button.children[0].text = self.text
        return super().refresh_view_attrs(rv, index, data)


class AgeRecycleView(RecycleView):
    """RecycleView для отображения списка возрастов."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bar_width = 0
        self.do_scroll_x = False

    def select_item(self, value):
        """Оповещает родительский поппер о выбранном возрасте."""
        if hasattr(self, 'parent_popup'):
            self.parent_popup.select_age(value)


class AgePickerPopup(Popup):
    """Всплывающее окно для выбора возраста."""

    def __init__(self, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Выберите ваш возраст"
        self.size_hint = (0.85, 0.65)
        self.auto_dismiss = True
        self.background = ""
        self.background_color = (1, 1, 1, 1)
        self._snap_event = None
        self._create_ui()

    def _create_ui(self):
        """Создаёт интерфейс: RecycleView + кнопка отмены."""
        root = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(16),
        )
        years = [{'text': str(i)} for i in range(15, 121)]
        self.rv = AgeRecycleView()
        self.rv.parent_popup = self
        self.rv.data = years
        self.rv.bind(scroll_y=self.on_scroll)

        footer = MDBoxLayout(size_hint_y=None, height=dp(56))
        footer.add_widget(MDBoxLayout())
        cancel_btn = MDButton(
            MDButtonText(
                text="Отмена",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
            ),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color=(0, 0, 0, 1),
            on_release=self.dismiss,
        )
        footer.add_widget(cancel_btn)
        footer.add_widget(MDBoxLayout())

        root.add_widget(self.rv)
        root.add_widget(footer)
        self.content = root

    def on_scroll(self, instance, value):
        """При прокрутке планируем снэп (прилипание) к ближайшему элементу."""
        if self._snap_event:
            self._snap_event.cancel()
        self._snap_event = Clock.schedule_once(self.snap_to_nearest, 0.15)

    def snap_to_nearest(self, *args):
        """Прилипает к ближайшему значению в списке."""
        total = len(self.rv.data)
        if total == 0:
            return
        scroll_y = self.rv.scroll_y
        index = round((1 - scroll_y) * (total - 1))
        index = max(0, min(index, total - 1))
        target_y = 1 - (index / (total - 1))
        Animation(scroll_y=target_y,
                  duration=0.15,
                  t='out_quad').start(self.rv)

    def select_age(self, age):
        """
        Вызывается при выборе возраста:
        закрывает поппер и вызывает callback.
        """
        self.dismiss()
        if self.callback:
            self.callback(age)

    def on_dismiss(self):
        """Отменяет запланированный снэп при закрытии."""
        if self._snap_event:
            self._snap_event.cancel()
        if hasattr(self, 'rv') and self.rv:
            self.rv.unbind(scroll_y=self.on_scroll)
        return super().on_dismiss()
