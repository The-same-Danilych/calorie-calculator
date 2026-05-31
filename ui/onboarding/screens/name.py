from kivy.lang import Builder
from kivy.properties import ObjectProperty
from ui.onboarding.screens.base import OnboardingStepScreen

KV_NM = """
<NameScreen>:
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
                text: "Как вас зовут?"
                font_style: "Display"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: name_input
                mode: "outlined"
                size_hint_x: 1
                pos_hint: {"center_x": 0.5}
                theme_line_color: "Custom"
                line_color_normal: (0, 0, 0, 1)
                line_color_focus: (0, 0, 0, 1)

                MDTextFieldHintText:
                    text: "Ваше имя"

                MDTextFieldMaxLengthText:
                    max_text_length: 100
                
                MDTextFieldHelperText:
                    text: "Зачем вам такое длинное имя?"
                    mode: "on_error"

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


class NameScreen(OnboardingStepScreen):
    flow = ObjectProperty(None)
    show_progress = True

    def validate(self) -> str | None:
        name = self.ids.name_input.text.strip()
        if len(name) > 100:
            return "Введите имя кароче 100 символов"
        if not name:
            return "Введите ваше имя"
        return None

    def save_to_flow(self):
        if self.flow:
            self.flow.data["name"] = self.ids.name_input.text.strip()

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
