from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ColorProperty
from kivy.animation import Animation
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp

KV_MACRO_BAR = """
<MacroBar>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(40)
    spacing: dp(12)
    padding: [0, dp(4), 0, dp(4)]

    MDLabel:
        text: root.label
        font_style: "Label"
        role: "large"
        size_hint_x: None
        width: dp(72)
        theme_text_color: "Custom"
        text_color: root.bar_color
        valign: "center"
        halign: "left"

    MDBoxLayout:
        orientation: "horizontal"
        size_hint_x: 1
        size_hint_y: None
        height: dp(8)
        pos_hint: {"center_y": 0.5}
        radius: [dp(4)]
        md_bg_color: 0.92, 0.92, 0.92, 1

        MDBoxLayout:
            id: fill
            size_hint_x: 0
            size_hint_y: 1
            radius: [dp(4)]
            md_bg_color: root.bar_color

    MDLabel:
        id: value_label
        text: root.value_text
        font_style: "Label"
        role: "medium"
        size_hint_x: None
        width: dp(80)
        theme_text_color: "Custom"
        text_color: 0.5, 0.5, 0.5, 1
        valign: "center"
        halign: "right"
"""

Builder.load_string(KV_MACRO_BAR)


class MacroBar(MDBoxLayout):
    label = StringProperty("Белки")
    bar_color = ColorProperty([0.36, 0.50, 0.83, 1])
    eaten = NumericProperty(0)
    goal = NumericProperty(1)

    @property
    def value_text(self) -> str:
        return f"{self.eaten:.0f} / {self.goal:.0f} г"

    def on_eaten(self, *_):
        self._animate()

    def on_goal(self, *_):
        self._animate()

    def _animate(self):
        if self.goal <= 0:
            return
        # Проверяем, что виджет fill уже создан
        fill = self.ids.get('fill')
        if not fill:
            return
        ratio = min(self.eaten / self.goal, 1.0)
        Animation.cancel_all(fill)
        Animation(size_hint_x=ratio, duration=0.5, t="out_cubic").start(fill)
        self.ids.value_label.text = self.value_text