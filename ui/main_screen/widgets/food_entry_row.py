from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp

KV_FOOD_ROW = """
<FoodEntryRow>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(52)
    padding: [dp(16), dp(4), dp(8), dp(4)]
    spacing: dp(8)

    MDBoxLayout:
        orientation: "vertical"
        size_hint_x: 1
        spacing: dp(2)

        MDLabel:
            text: root.food_name
            font_style: "Body"
            role: "medium"
            theme_text_color: "Custom"
            text_color: 0, 0, 0, 0.9
            size_hint_y: None
            height: dp(22)
            shorten: True
            shorten_from: "right"

        MDLabel:
            text: root.grams_text
            font_style: "Label"
            role: "medium"
            theme_text_color: "Custom"
            text_color: 0, 0, 0, 0.45
            size_hint_y: None
            height: dp(18)

    MDLabel:
        text: root.cal_text
        font_style: "Label"
        role: "large"
        size_hint_x: None
        width: dp(72)
        halign: "right"
        valign: "center"
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 0.6

    MDIconButton:
        icon: "close"
        size_hint: None, None
        size: dp(36), dp(36)
        pos_hint: {"center_y": 0.5}
        theme_icon_color: "Custom"
        icon_color: 0, 0, 0, 0.25
        on_release: root.on_delete()
"""

Builder.load_string(KV_FOOD_ROW)


class FoodEntryRow(MDBoxLayout):
    food_name = StringProperty("")
    grams = NumericProperty(0)
    calories = NumericProperty(0)
    entry_id = NumericProperty(0)
    on_delete_callback = ObjectProperty(None, allownone=True)

    @property
    def grams_text(self) -> str:
        return f"{self.grams:.0f} г"

    @property
    def cal_text(self) -> str:
        return f"{self.calories:.0f} ккал"

    def on_delete(self):
        if self.on_delete_callback:
            self.on_delete_callback(self.entry_id)