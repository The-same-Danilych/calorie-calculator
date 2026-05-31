from kivy.lang import Builder
from kivy.properties import ObjectProperty
from ui.onboarding.screens.base import OnboardingStepScreen

KV_BODY = """
<BodyScreen>:
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
                text: "Укажите пожалуйста ваш рост и вес"
                font_style: "Display"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: (0, 0, 0, 1)
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: height_input
                mode: "outlined"
                size_hint_x: 1
                pos_hint: {"center_x": 0.5}
                theme_line_color: "Custom"
                line_color_normal: (0, 0, 0, 1)
                line_color_focus: (0, 0, 0, 1)
                input_filter: "float"
                on_text: root.on_field_change()
                
                MDTextFieldHintText:
                    text: "Рост (см)"
                
                MDTextFieldHelperText:
                    id: height_helper
                    text: ""
                    mode: "on_error"

            MDTextField:
                id: weight_input
                mode: "outlined"
                size_hint_x: 1
                pos_hint: {"center_x": 0.5}
                theme_line_color: "Custom"
                line_color_normal: (0, 0, 0, 1)
                line_color_focus: (0, 0, 0, 1)
                input_filter: "float"
                on_text: root.on_field_change()
                
                MDTextFieldHintText:
                    text: "Вес (кг)"
                
                MDTextFieldHelperText:
                    id: weight_helper
                    text: ""
                    mode: "on_error"

        Widget:
            size_hint_y: 1

        MDButton:
            id: next_btn
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

Builder.load_string(KV_BODY)


class BodyScreen(OnboardingStepScreen):
    flow = ObjectProperty(None)
    show_progress = True

    def on_enter(self):
        super().on_enter()
        self.validate_field("height")
        self.validate_field("weight")
        self._update_next_button()

    def on_field_change(self):
        self.validate_field("height")
        self.validate_field("weight")
        self._update_next_button()

    def validate_field(self, field: str) -> bool:
        if field == "height":
            text = self.ids.height_input.text.strip()
            helper = self.ids.height_helper
        else:
            text = self.ids.weight_input.text.strip()
            helper = self.ids.weight_helper

        if not text:
            helper.text = "Поле обязательно для заполнения"
            helper.mode = "on_error"
            return False

        text = text.replace(",", ".")
        try:
            value = float(text)
        except ValueError:
            helper.text = "Введите число (например, 175.5)"
            helper.mode = "on_error"
            return False

        if field == "height":
            if 50 <= value <= 300:
                helper.text = ""
                helper.mode = "persistent"
                if self.flow:
                    self.flow.data["height_cm"] = value
                return True
            else:
                helper.text = "Рост должен быть от 50 до 300 см"
                helper.mode = "on_error"
                return False
        else:
            if 20 <= value <= 500:
                helper.text = ""
                helper.mode = "persistent"
                if self.flow:
                    self.flow.data["weight_kg"] = value
                return True
            else:
                helper.text = "Вес должен быть от 20 до 500 кг"
                helper.mode = "on_error"
                return False

    def _update_next_button(self):
        height_valid = self.validate_field("height")
        weight_valid = self.validate_field("weight")
        self.ids.next_btn.disabled = not (height_valid and weight_valid)

    def validate(self) -> str | None:
        if not self.validate_field("height"):
            return "Укажите корректный рост (50–300 см)"
        if not self.validate_field("weight"):
            return "Укажите корректный вес (20–500 кг)"
        return None

    def save_to_flow(self):
        if not self.flow:
            return
        try:
            height_text = self.ids.height_input.text.strip().replace(",", ".")
            weight_text = self.ids.weight_input.text.strip().replace(",", ".")
            self.flow.data["height_cm"] = float(height_text)
            self.flow.data["weight_kg"] = float(weight_text)
        except (ValueError, AttributeError):
            pass

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