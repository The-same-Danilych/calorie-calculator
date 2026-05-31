from ui.onboarding.screens.base import OnboardingStepScreen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from config import image

KV_GR = """
<GreetingScreen>:
    show_progress: False
    
    FitImage:
        source: root.get_image_path()
        size_hint: 1, 0.5
        pos_hint: {"top": 1}
        fit_mode: "fill"

    MDBoxLayout:
        orientation: "vertical"
        size_hint: 1, 0.6
        pos_hint: {"bottom": 1}
        md_bg_color: (1, 1, 1, 1)
        radius: [36, 36, 0, 0]
        padding: dp(24), dp(24)

        Widget:
            size_hint_y: 1

        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            spacing: dp(12)

            MDLabel:
                text: "Удобный учет питания"
                font_style: "Display"
                role: "small"
                halign: "center"
                theme_text_color: "Primary"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)

            MDLabel:
                text: "Давай познакомимся, чтобы рассчитать твою норму калорий"
                font_style: "Body"
                role: "large"
                halign: "center"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 0.85)

            MDLabel:
                text: "Получите персональный план за минуту"
                font_style: "Body"
                role: "small"
                halign: "center"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 0.8)

        Widget:
            size_hint_y: 0.5

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
                text: "Начать"
                theme_text_color: "Custom"
                text_color: (1, 1, 1, 1)
                            
            MDButtonIcon:
                icon: "arrow-right"
                theme_icon_color: "Custom"
                icon_color: (1, 1, 1, 1)

        Widget:
            size_hint_y: 0.2
"""

Builder.load_string(KV_GR)


class GreetingScreen(OnboardingStepScreen):
    flow = ObjectProperty(None)
    show_progress = False

    def get_image_path(self) -> str:
        return image("greeting_image.png")

    def go_next(self):
        if self.flow:
            self.flow.go_next()
