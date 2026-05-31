from kivy.lang import Builder
from kivy.properties import ObjectProperty
from ui.onboarding.screens.base import OnboardingStepScreen
from ui.onboarding.screens.age_picker import AgePickerPopup

KV_NM = """
<YearScreen>:
    MDBoxLayout:
        orientation: "vertical"
        size_hint: 1, 1
        padding: dp(24), 0, dp(24), dp(24)
        spacing: dp(20)
        md_bg_color: (1, 1, 1, 1)

        ProgressBarHeader:
            id: progress_header
            value: 0

        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: dp(56)
            
            MDIconButton:
                icon: "arrow-left"
                pos_hint: {"x": 0, "top": 1}
                size_hint: None, None
                size: dp(48), dp(48)
                theme_icon_color: "Custom"
                icon_color: (0, 0, 0, 1)
                on_release: root.go_back()

        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            spacing: dp(30)

            MDLabel:
                text: "Сколько вам полных лет?"
                font_style: "Display"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]

            MDButton:
                id: age_selector
                style: "outlined"
                size_hint_x: 1
                size_hint_y: None
                height: dp(56)
                pos_hint: {"center_x": 0.5}
                theme_line_color: "Custom"
                line_color_normal: (0, 0, 0, 1)
                on_release: root.show_age_picker()

                MDButtonText:
                    id: age_text
                    text: "Нажмите, чтобы выбрать"
                    theme_text_color: "Custom"
                    text_color: (0, 0, 0, 1)

        Widget:
            size_hint_y: 1

        MDButton:
            style: "filled"
            size_hint_x: 0.9
            size_hint_y: None
            height: dp(52)
            pos_hint: {"center_x": 0.5}
            theme_bg_color: "Custom"
            md_bg_color: (0, 0, 0, 1)
            on_release: root.go_next()
            
            MDButtonText:
                text: "Продолжить"
                theme_text_color: "Custom"
                text_color: (1, 1, 1, 1)
"""

Builder.load_string(KV_NM)


class YearScreen(OnboardingStepScreen):
    flow = ObjectProperty(None)
    show_progress = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.age_picker = None

    def show_age_picker(self):

        if self.age_picker is None:
            self.age_picker = AgePickerPopup(
                callback=self.on_age_selected
            )

        self.age_picker.open()

    def on_age_selected(self, age: str):

        self.ids.age_text.text = age

        if self.flow:
            self.flow.data["years"] = int(age)

    def validate(self):

        age_text = self.ids.age_text.text.strip()

        if age_text == "Нажмите, чтобы выбрать":
            return "Пожалуйста, выберите ваш возраст"

        try:
            age = int(age_text)

            if not 15 <= age <= 120:
                return "Возраст должен быть от 15 до 120 лет"

        except ValueError:
            return "Пожалуйста, выберите корректный возраст"

        return None

    def save_to_flow(self):

        if not self.flow:
            return

        age = int(self.ids.age_text.text)

        self.flow.data["years"] = age

    def go_next(self):
        if self.flow:
            error = self.validate()
            if error:
                self.show_error(error)
                return
            self.save_to_flow()
            self.flow.go_next()

    def go_back(self):
        if self.flow:
            self.flow.go_back()
