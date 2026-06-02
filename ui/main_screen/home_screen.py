"""Главный экран дневника: отображение приёмов пищи, прогресса, календарь."""

from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import (
    MDListItem, MDListItemHeadlineText,
    MDListItemTrailingIcon,
    MDListItemSupportingText
)
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.pickers import MDModalDatePicker, MDModalInputDatePicker
from kivymd.uix.behaviors import RotateBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.button import MDFabButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
)
from kivymd.uix.navigationdrawer import (
    MDNavigationDrawer, MDNavigationDrawerMenu,
    MDNavigationDrawerHeader, MDNavigationDrawerLabel, MDNavigationDrawerItem
)
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText

from services.diary_service import get_day_summary, delete_entry
from services.user_service import get_user_async, delete_user_async
from utils.async_db import run_in_background
from database.engine import delete_database

from datetime import date

KV_HOME = """
#:import dp kivy.metrics.dp

<HomeScreen>:
    RelativeLayout:

        MDNavigationDrawer:
            id: nav_drawer
            drawer_type: "modal"
            radius: 0
            width: dp(300)
            size_hint: None, 1
            md_bg_color: (1, 1, 1, 1)
            pos_hint: {"x": 0, "top": 1}

            MDNavigationDrawerMenu:

                MDNavigationDrawerHeader:
                    title: "Меню"
                    spacing: "4dp"
                    padding: ["12dp", "12dp", "12dp", "12dp"]

                MDNavigationDrawerItem:
                    text: "Изменить профиль"
                    icon: "account-edit"
                    on_release: root.open_edit_profile_dialog(); nav_drawer.set_state("close")

                MDNavigationDrawerItem:
                    text: "Анализ"
                    icon: "chart-line"
                    on_release: root.open_analysis(); nav_drawer.set_state("close")

                MDNavigationDrawerItem:
                    text: "Удалить аккаунт"
                    icon: "delete"
                    on_release: root.confirm_delete_account(); nav_drawer.set_state("close")

        MDBoxLayout:
            orientation: "vertical"
            md_bg_color: (1, 1, 1, 1)
            size_hint: 1, 1

        MDBoxLayout:
            orientation: "vertical"
            md_bg_color: (1, 1, 1, 1)
            size_hint: 1, 1

            MDTopAppBar:
                type: "small"
                size_hint_x: .9
                pos_hint: {"center_x": .5}
                theme_bg_color: "Custom"
                md_bg_color: (1, 1, 1, 1)
                elevation: 0

                MDTopAppBarLeadingButtonContainer:
                    MDActionTopAppBarButton:
                        icon: "menu"
                        id: menu_button
                        on_release: root.toggle_nav_drawer()
                MDTopAppBarTitle:
                    text: "Дневник"
                    halign: "center"

                MDTopAppBarTrailingButtonContainer:
                    MDActionTopAppBarButton:
                        icon: "calendar"
                        on_release: root.show_modal_date_picker()

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: dp(48)
                padding: [dp(16), dp(8), dp(16), dp(8)]
                md_bg_color: (0.98, 0.98, 0.98, 1)

                MDLabel:
                    id: date_label
                    text: ""
                    font_style: "Label"
                    role: "medium"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: (0, 0, 0, 0.7)

            MDScrollView:
                do_scroll_x: False
                bar_width: 0

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(16)
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(16), dp(16), dp(16), dp(16)]

                    MDCard:
                        size_hint_x: 1
                        size_hint_y: None
                        height: dp(320)
                        style: "outlined"
                        theme_bg_color: "Custom"
                        md_bg_color: (1, 1, 1, 1)
                        ripple_behavior: False
                        focus_behavior: False
                        elevation: 0

                        MDBoxLayout:
                            orientation: "vertical"
                            spacing: dp(16)
                            padding: dp(16)

                            MDBoxLayout:
                                orientation: "horizontal"
                                spacing: dp(16)
                                size_hint_y: None
                                height: dp(120)
                                theme_bg_color: "Custom"
                                md_bg_color: (1, 1, 1, 1)

                                MDExCircularProgressIndicator:
                                    id: calories_progress
                                    size_hint: None, None
                                    width: dp(120)
                                    height: dp(120)
                                    active_track_color: (0.9, 0, 0.2, 1)
                                    inactive_track_color: (0.85, 0.85, 0.85, 1)
                                    value: 0
                                    amplitude: dp(1)

                                MDBoxLayout:
                                    orientation: "vertical"
                                    spacing: dp(4)
                                    pos_hint: {"center_y": 0.5}

                                    MDLabel:
                                        id: calories_goal
                                        text: "0 / 0 ккал"
                                        font_style: "Title"
                                        role: "large"
                                        theme_text_color: "Custom"
                                        text_color: (0, 0, 0, 1)
                                        halign: "center"

                            MDBoxLayout:
                                orientation: "vertical"
                                spacing: dp(4)
                                theme_bg_color: "Custom"
                                md_bg_color: (1, 1, 1, 1)

                                MDLabel:
                                    text: "Белки"
                                    font_style: "Title"
                                    role: "small"
                                    theme_text_color: "Custom"
                                    text_color: (0, 0, 0, 1)

                                MDExLinearProgressIndicator:
                                    id: protein_indicator
                                    active_track_color: (1, 0, 0, 1)
                                    inactive_track_color: (0.85, 0.85, 0.85, 1)
                                    value: 0
                                    amplitude: dp(0)

                                MDLabel:
                                    id: protein_goal
                                    text: "0 / 0 г"
                                    role: "small"
                                    theme_text_color: "Custom"
                                    text_color: (0, 0, 0, 0.9)

                            MDBoxLayout:
                                orientation: "vertical"
                                spacing: dp(4)
                                theme_bg_color: "Custom"
                                md_bg_color: (1, 1, 1, 1)

                                MDLabel:
                                    text: "Жиры"
                                    font_style: "Title"
                                    role: "small"
                                    theme_text_color: "Custom"
                                    text_color: (0, 0, 0, 1)

                                MDExLinearProgressIndicator:
                                    id: fat_indicator
                                    active_track_color: (0, 1, 0, 1)
                                    inactive_track_color: (0.85, 0.85, 0.85, 1)
                                    value: 0
                                    amplitude: dp(0)

                                MDLabel:
                                    id: fat_goal
                                    text: "0 / 0 г"
                                    role: "small"
                                    theme_text_color: "Custom"
                                    text_color: (0, 0, 0, 0.9)

                            MDBoxLayout:
                                orientation: "vertical"
                                spacing: dp(4)
                                theme_bg_color: "Custom"
                                md_bg_color: (1, 1, 1, 1)

                                MDLabel:
                                    text: "Углеводы"
                                    font_style: "Title"
                                    role: "small"
                                    theme_text_color: "Custom"
                                    text_color: (0, 0, 0, 1)

                                MDExLinearProgressIndicator:
                                    id: carb_indicator
                                    active_track_color: (0, 0, 1, 1)
                                    inactive_track_color: (0.85, 0.85, 0.85, 1)
                                    value: 0
                                    amplitude: dp(0)

                                MDLabel:
                                    id: carb_goal
                                    text: "0 / 0 г"
                                    role: "small"
                                    theme_text_color: "Custom"
                                    text_color: (0, 0, 0, 0.9)

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: dp(16)
                        size_hint_y: None
                        height: self.minimum_height
                        padding: [dp(16), dp(16), dp(16), dp(16)]

                        MDExpansionPanel:
                            id: panel_breakfast
                            size_hint_y: None
                            height: self.minimum_height

                            MDExpansionPanelHeader:
                                size_hint_y: None
                                height: dp(56)

                                MDListItem:
                                    ripple_effect: True
                                    theme_bg_color: "Custom"
                                    md_bg_color: (0.95, 0.95, 0.95, 1)

                                    MDListItemSupportingText:
                                        id: breakfast_header
                                        text: "Завтрак (0 ккал)"

                                    TrailingPressedIconButton:
                                        id: chevron_breakfast
                                        icon: "chevron-right"
                                        on_release: root.tap_expansion_chevron(panel_breakfast, chevron_breakfast, "breakfast")

                            MDExpansionPanelContent:
                                id: breakfast_content
                                orientation: "vertical"
                                padding: "12dp", 0, "12dp", "12dp"
                                size_hint_y: None
                                height: self.minimum_height

                        MDExpansionPanel:
                            id: panel_lunch
                            size_hint_y: None
                            height: self.minimum_height

                            MDExpansionPanelHeader:
                                size_hint_y: None
                                height: dp(56)

                                MDListItem:
                                    ripple_effect: True
                                    theme_bg_color: "Custom"
                                    md_bg_color: (0.95, 0.95, 0.95, 1)

                                    MDListItemSupportingText:
                                        id: lunch_header
                                        text: "Обед (0 ккал)"

                                    TrailingPressedIconButton:
                                        id: chevron_lunch
                                        icon: "chevron-right"
                                        on_release: root.tap_expansion_chevron(panel_lunch, chevron_lunch, "lunch")

                            MDExpansionPanelContent:
                                id: lunch_content
                                orientation: "vertical"
                                padding: "12dp", 0, "12dp", "12dp"
                                size_hint_y: None
                                height: self.minimum_height

                        MDExpansionPanel:
                            id: panel_dinner
                            size_hint_y: None
                            height: self.minimum_height

                            MDExpansionPanelHeader:
                                size_hint_y: None
                                height: dp(56)

                                MDListItem:
                                    ripple_effect: True
                                    theme_bg_color: "Custom"
                                    md_bg_color: (0.95, 0.95, 0.95, 1)

                                    MDListItemSupportingText:
                                        id: dinner_header
                                        text: "Ужин (0 ккал)"

                                    TrailingPressedIconButton:
                                        id: chevron_dinner
                                        icon: "chevron-right"
                                        on_release: root.tap_expansion_chevron(panel_dinner, chevron_dinner, "dinner")

                            MDExpansionPanelContent:
                                id: dinner_content
                                orientation: "vertical"
                                padding: "12dp", 0, "12dp", "12dp"
                                size_hint_y: None
                                height: self.minimum_height

                        MDExpansionPanel:
                            id: panel_snack
                            size_hint_y: None
                            height: self.minimum_height

                            MDExpansionPanelHeader:
                                size_hint_y: None
                                height: dp(56)

                                MDListItem:
                                    ripple_effect: True
                                    theme_bg_color: "Custom"
                                    md_bg_color: (0.95, 0.95, 0.95, 1)

                                    MDListItemSupportingText:
                                        id: snack_header
                                        text: "Перекус (0 ккал)"

                                    TrailingPressedIconButton:
                                        id: chevron_snack
                                        icon: "chevron-right"
                                        on_release: root.tap_expansion_chevron(panel_snack, chevron_snack, "snack")

                            MDExpansionPanelContent:
                                id: snack_content
                                orientation: "vertical"
                                padding: "12dp", 0, "12dp", "12dp"
                                size_hint_y: None
                                height: self.minimum_height

                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(100)

        MDFabButton:
            id: add_meal
            icon: "plus"
            theme_icon_color: "Custom"
            icon_color: (1, 1, 1, 1)
            style: "large"
            pos_hint: {"center_x": 0.5, "bottom": 1}
            theme_bg_color: "Custom"
            md_bg_color: (0, 0, 0, 1)
            on_release: root.on_fab_pressed()
"""

Builder.load_string(KV_HOME)


class TrailingPressedIconButton(ButtonBehavior,
                                RotateBehavior,
                                MDListItemTrailingIcon):
    """Иконка-кнопка с анимацией поворота для раскрытия панели приёма пищи."""
    pass


class TrailingDeleteIconButton(ButtonBehavior,
                               MDListItemTrailingIcon):
    """Кликабельная иконка удаления в списке приёмов пищи."""
    pass


class HomeScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None
        self.totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        self.meals = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
        self._loading = False
        self.current_date = date.today()
        self.menu = None

    def on_enter(self):
        """При входе на экран загружаем данные пользователя и дневник."""
        self.load_data()

    def load_data(self, target_date: date = None):
        """Загружает данные для указанной даты (или сегодняшней)."""
        if self._loading:
            return
        self._loading = True
        if target_date is not None:
            self.current_date = target_date
        self.update_date_label()
        get_user_async(self.on_user_loaded)

    def on_user_loaded(self, user):
        """Обработчик загрузки пользователя."""
        self.user = user
        if user:
            self.update_goals_display()
            run_in_background(
                lambda: get_day_summary(user.id, self.current_date),
                on_success=self.on_summary_loaded,
                on_error=self.on_load_error
            )
        else:
            self.manager.current = "onboarding"
            self._loading = False

    def on_summary_loaded(self, summary):
        """Обработчик загрузки сводки за день."""
        self.totals = summary["totals"]
        self.meals = summary["meals"]
        self.update_progress_bars()
        self.update_meal_panels()
        self._loading = False

        total_cal = self.totals["calories"]
        all_empty = all(len(v) == 0 for v in self.meals.values())
        if total_cal == 0 and all_empty and self.current_date != date.today():
            empty_date = self.current_date
            self.current_date = date.today()
            self.show_empty_day_warning(empty_date)
            self.load_data()

    def show_empty_day_warning(self, empty_date: date):
        """Предупреждение, что за выбранную дату нет записей."""
        MDSnackbar(
            MDSnackbarText(
                text=f"Нет записей за {empty_date.strftime('%d.%m.%Y')}. Показан сегодняшний день"),
            duration=2.5,
            pos_hint={"center_x": 0.5, "center_y": 0.1},
        ).open()

    def update_date_label(self):
        """Обновляет отображение текущей даты."""
        if hasattr(self.ids, "date_label"):
            self.ids.date_label.text = self.current_date.strftime("%d.%m.%Y")

    def on_load_error(self, error):
        """Ошибка загрузки дневника."""
        self._loading = False
        MDSnackbar(MDSnackbarText(
            text="Не удалось загрузить дневник"), duration=2).open()

    def update_goals_display(self):
        """Обновляет круговой и линейные индикаторы КБЖУ."""
        if not self.user:
            return
        cal_goal = self.user.calorie_goal
        cal_current = self.totals["calories"]
        self.ids.calories_goal.text = f"{int(cal_current)} / {int(cal_goal)} ккал"
        self.ids.calories_progress.value = (
            cal_current / cal_goal * 100) if cal_goal else 0

        prot_goal = self.user.protein_goal
        prot_current = self.totals["protein"]
        self.ids.protein_goal.text = f"{int(prot_current)} / {int(prot_goal)} г"
        self.ids.protein_indicator.value = (
            prot_current / prot_goal * 100) if prot_goal else 0

        fat_goal = self.user.fat_goal
        fat_current = self.totals["fat"]
        self.ids.fat_goal.text = f"{int(fat_current)} / {int(fat_goal)} г"
        self.ids.fat_indicator.value = (
            fat_current / fat_goal * 100) if fat_goal else 0

        carb_goal = self.user.carb_goal
        carb_current = self.totals["carbs"]
        self.ids.carb_goal.text = f"{int(carb_current)} / {int(carb_goal)} г"
        self.ids.carb_indicator.value = (
            carb_current / carb_goal * 100) if carb_goal else 0

    def update_progress_bars(self):
        """Обёртка для обновления всех индикаторов."""
        self.update_goals_display()

    def update_meal_panels(self):
        """Заполняет панели приёмов пищи записями из дневника."""
        for meal_type in ["breakfast", "lunch", "dinner", "snack"]:
            entries = self.meals.get(meal_type, [])
            total_cal = sum(e.calories for e in entries)
            header_text = {
                "breakfast": "Завтрак",
                "lunch": "Обед",
                "dinner": "Ужин",
                "snack": "Перекус"
            }[meal_type]
            header_label = self.ids[f"{meal_type}_header"]
            if header_label:
                header_label.text = f"{header_text} ({int(total_cal)} ккал)"

            content = self.ids[f"{meal_type}_content"]
            content.clear_widgets()

            panel = self.ids[f"panel_{meal_type}"]
            panel.disabled = (len(entries) == 0)

            for entry in entries:
                item = MDListItem()
                item.add_widget(
                    MDListItemHeadlineText(
                        text=f"{entry.food_item.name} — {int(entry.grams)} г"
                    )
                )
                item.add_widget(
                    MDListItemSupportingText(
                        text=f"{int(entry.calories)} ккал • "
                        f"{int(entry.protein)} г б • "
                        f"{int(entry.fat)} г ж • "
                        f"{int(entry.carbs)} г у"
                    )
                )
                action_box = MDBoxLayout(
                    orientation="horizontal",
                    spacing=dp(8),
                    size_hint=(None, None),
                    size=(dp(80), dp(48)),
                    pos_hint={"center_y": 0.5}
                )
                edit_btn = TrailingDeleteIconButton(
                    icon="pencil",
                    theme_icon_color="Custom",
                    icon_color=(0, 0, 0, 0.7),
                    on_release=lambda x, e_id=entry.id: self.open_edit_entry(
                        e_id)
                )
                delete_btn = TrailingDeleteIconButton(
                    icon="delete",
                    theme_icon_color="Custom",
                    icon_color=(0.8, 0.2, 0.2, 1),
                    on_release=lambda x, e_id=entry.id: self.delete_entry(e_id)
                )
                action_box.add_widget(edit_btn)
                action_box.add_widget(delete_btn)
                item.add_widget(action_box)
                content.add_widget(item)

    def delete_entry(self, entry_id: int):
        """Удаляет запись из дневника и перезагружает данные."""
        run_in_background(
            lambda: delete_entry(entry_id),
            on_success=lambda _: self.load_data(),
            on_error=lambda e: print(f"Ошибка удаления: {e}")
        )

    def open_edit_entry(self, entry_id: int):
        """Открывает экран редактирования для указанной записи."""
        if hasattr(self, "manager") and self.manager.has_screen("add_food"):
            add_screen = self.manager.get_screen("add_food")
            add_screen.open_for_edit(
                entry_id=entry_id,
                user_id=self.user.id if self.user else 1,
                on_done=lambda entry: self.refresh()
            )
            self.manager.current = "add_food"

    def refresh(self):
        """Принудительная перезагрузка."""
        self.load_data()

    def tap_expansion_chevron(self, panel, chevron, meal_type):
        """Обработчик нажатия на шеврон панели приёма пищи."""
        if panel.disabled:
            return
        if not panel.is_open:
            panel.open()
            panel.set_chevron_down(chevron)
        else:
            panel.close()
            panel.set_chevron_up(chevron)

    def show_modal_date_picker(self, *args):
        """Показывает календарь для выбора даты."""
        date_dialog = MDModalDatePicker(scrim_color=(0, 0, 0, 1))
        date_dialog.bind(on_edit=self.on_edit,
                         on_ok=self.on_date_picker_ok,
                         on_cancel=self.on_cancel)
        date_dialog.open()

    def show_modal_input_date_picker(self, *args):
        """Показывает текстовый диалог ввода даты (резервный вариант)."""
        date_dialog = MDModalInputDatePicker(scrim_color=(0, 0, 0, 1))
        date_dialog.bind(
            on_edit=self.on_edit,
            on_ok=self.on_input_date_picker_ok,
            on_cancel=self.on_cancel
        )
        date_dialog.open()

    def on_date_picker_ok(self, instance_date_picker):
        """Обработчик выбора даты из календаря."""
        try:
            selected_date = instance_date_picker.get_date()[0]
            if selected_date:
                self.load_data(selected_date)
        except Exception as e:
            print(f"Ошибка получения даты из календаря: {e}")
        instance_date_picker.dismiss()

    def on_input_date_picker_ok(self, instance_date_picker):
        """Обработчик ввода даты вручную."""
        try:
            selected_date = instance_date_picker.get_date()[0]
            if selected_date:
                self.load_data(selected_date)
            else:
                raise ValueError("Не удалось распознать дату")
        except Exception:
            MDSnackbar(
                MDSnackbarText(
                    text="Неверный формат даты. Используйте ДД/ММ/ГГГГ"),
                duration=2.5,
                pos_hint={"center_x": 0.5, "center_y": 0.1},
            ).open()
            return
        instance_date_picker.dismiss()

    def on_edit(self, instance_date_picker):
        """Переключение с графического календаря на текстовый ввод."""
        instance_date_picker.dismiss()
        Clock.schedule_once(self.show_modal_input_date_picker, 0.2)

    def on_cancel(self, instance_date_picker):
        instance_date_picker.dismiss()

    def on_fab_pressed(self):
        """Кнопка добавления пищи: открывает экран AddFoodScreen."""
        if hasattr(self, "manager") and self.manager.has_screen("add_food"):
            add_screen = self.manager.get_screen("add_food")
            add_screen.open_for(
                meal_key="breakfast",
                user_id=self.user.id if self.user else 1,
                on_done=lambda entry: self.refresh()
            )
            self.manager.current = "add_food"

    def open_edit_profile_dialog(self):
        """Переход на экран редактирования профиля."""
        if hasattr(self, "manager") and self.manager.has_screen("edit_profile"):
            self.menu_drawer.dismiss()
            self.manager.current = "edit_profile"
        else:
            MDSnackbar(MDSnackbarText(
                text="Экран редактирования не найден"), duration=2).open()

    def confirm_delete_account(self):
        """Диалог подтверждения удаления аккаунта."""
        if not hasattr(self, 'delete_account_dialog'):
            self.delete_account_dialog = MDDialog(
                MDDialogHeadlineText(
                    text="Подтверждение удаления", halign="left"),
                MDDialogSupportingText(
                    text="Вы уверены, что хотите удалить аккаунт? Это действие необратимо.",
                    halign="left"),
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(MDButtonText(text="Отмена"), style="text",
                             on_release=lambda x: self.delete_account_dialog.dismiss()),
                    MDButton(MDButtonText(text="Удалить"), style="text",
                             on_release=lambda x: self.delete_account()),
                    spacing="8dp",
                ),
            )
        self.delete_account_dialog.open()

    def delete_account(self):
        """Выполняет удаление пользователя и всей базы данных."""
        if not self.user:
            return
        if hasattr(self, 'delete_account_dialog'):
            self.delete_account_dialog.dismiss()

        run_in_background(
            lambda: delete_user_async(self.user.id),
            on_success=lambda _: self._after_user_deleted(),
            on_error=lambda e: MDSnackbar(MDSnackbarText(
                text=f"Ошибка удаления: {e}"), duration=2).open()
        )

    def _after_user_deleted(self):
        """
        Вызывается после успешного удаления пользователя:
        удаляем БД и переходим на онбординг.
        """
        delete_database()
        MDSnackbar(MDSnackbarText(text="Аккаунт и база данных удалены"),
                   duration=2).open()
        self.manager.current = "splash"

    def on_account_deleted(self):
        """После удаления аккаунта переходим на онбординг."""
        MDSnackbar(MDSnackbarText(text="Аккаунт удалён"), duration=2).open()
        self.manager.current = ""

    def open_analysis(self):
        """Переход на экран статистики."""
        if hasattr(self, "manager") and self.manager.has_screen("analysis"):
            self.menu_drawer.dismiss()
            self.manager.current = "analysis"
        else:
            MDSnackbar(MDSnackbarText(
                text="Экран анализа не найден"), duration=2).open()

    def toggle_nav_drawer(self):
        """
        Открывает/закрывает боковое меню
        (через выпадающее меню, так как навигационный ящик в KV уже есть).
        """
        if hasattr(self, 'menu_drawer'):
            self.menu_drawer.dismiss()
        menu_items = [
            {"text": "Изменить профиль",
                "on_release": lambda: self.open_edit_profile_dialog()},
            {"text": "Анализ", "on_release": lambda: self.open_analysis()},
            {"text": "Удалить аккаунт",
                "on_release": lambda: self.confirm_delete_account()},
        ]
        self.menu_drawer = MDDropdownMenu(
            caller=self.ids.get('menu_button', None),
            items=menu_items,
            position="auto",
        )
        self.menu_drawer.open()
