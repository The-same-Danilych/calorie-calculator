from kivy.lang import Builder
from kivy.properties import ObjectProperty
from ui.onboarding.screens.base import OnboardingStepScreen
from kivy.animation import Animation
from ui.onboarding.screens.progress_bar import ProgressBarHeader

KV_GENDER = """
<GenderScreen>:
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
            spacing: dp(40)

            MDLabel:
                text: "Ваш пол"
                font_style: "Display"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]

            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                spacing: dp(16)
                pos_hint: {"center_x": 0.5}

                # Мужской
                MDBoxLayout:
                    orientation: "horizontal"
                    adaptive_height: True
                    spacing: dp(16)
                    size_hint_x: 1
                    
                    MDCheckbox:
                        id: male_checkbox
                        group: "gender_group"
                        size_hint: None, None
                        size: dp(48), dp(48)
                        color_active: (0, 0, 0, 1)
                        color_inactive: (0, 0, 0, 0.54)
                        on_active: root.on_gender_selected("male", self.active)
                    
                    MDLabel:
                        text: "Мужской"
                        font_style: "Body"
                        role: "large"
                        size_hint_x: 1
                        adaptive_height: True
                        pos_hint: {"center_y": 0.5}
                        theme_text_color: "Primary"

                # Женский
                MDBoxLayout:
                    orientation: "horizontal"
                    adaptive_height: True
                    spacing: dp(16)
                    size_hint_x: 1
                    
                    MDCheckbox:
                        id: female_checkbox
                        group: "gender_group"
                        size_hint: None, None
                        size: dp(48), dp(48)
                        color_active: (0, 0, 0, 1)
                        color_inactive: (0, 0, 0, 0.54)
                        on_active: root.on_gender_selected("female", self.active)
                    
                    MDLabel:
                        text: "Женский"
                        font_style: "Body"
                        role: "large"
                        size_hint_x: 1
                        adaptive_height: True
                        pos_hint: {"center_y": 0.5}
                        theme_text_color: "Primary"

        Widget:
            size_hint_y: 1

        MDButton:
            id: continue_btn
            style: "filled"
            size_hint_x: 0.9
            size_hint_y: None
            height: dp(52)
            pos_hint: {"center_x": 0.5}
            theme_bg_color: "Custom"
            md_bg_color: (0, 0, 0, 1)
            disabled: True
            on_release: root.go_next()
            
            MDButtonText:
                text: "Продолжить"
                theme_text_color: "Custom"
                text_color: (1, 1, 1, 1)
"""

Builder.load_string(KV_GENDER)


class GenderScreen(OnboardingStepScreen):
    flow = ObjectProperty(None)
    show_progress = True
    selected_gender = None

    def on_enter(self):
        super().on_enter()
        self.update_progress()

        if self.flow and self.flow.data.get("gender"):
            self.selected_gender = self.flow.data["gender"]
            if self.selected_gender == "male":
                self.ids.male_checkbox.active = True
            elif self.selected_gender == "female":
                self.ids.female_checkbox.active = True
            self.ids.continue_btn.disabled = False

    def on_gender_selected(self, gender: str, is_active: bool):
        if is_active:
            self.selected_gender = gender
            self.ids.continue_btn.disabled = False
            self.save_to_flow()

    def validate(self) -> str | None:
        if not self.selected_gender:
            return "Выберите ваш пол"
        return None

    def save_to_flow(self):
        if self.flow and self.selected_gender:
            self.flow.data["gender"] = self.selected_gender

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
