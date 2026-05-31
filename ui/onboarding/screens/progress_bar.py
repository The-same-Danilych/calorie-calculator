from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.animation import Animation

KV = """
<ProgressBarHeader>:
    size_hint_y: None
    height: dp(40)
    padding: [dp(16), dp(24), dp(16), 0]

    MDExLinearProgressIndicator:
        id: progress
        size_hint_x: 1
        size_hint_y: None
        height: dp(8)
        pos_hint: {"center_y": 0.5}
        determinate: True
        active_track_color: (0, 0, 0, 1)
        inactive_track_color: (0.85, 0.85, 0.85, 1)
        value: 0
        amplitude: 0
"""

Builder.load_string(KV)


class ProgressBarHeader(BoxLayout):
    value = NumericProperty(0)

    def set_value(self, value: float, animated: bool = True, duration: float = 0.5):
        progress_bar = self.ids.progress

        if animated:
            Animation.cancel_all(progress_bar)
            anim = Animation(value=value, duration=duration, t="out_cubic")
            anim.start(progress_bar)
        else:
            progress_bar.value = value
