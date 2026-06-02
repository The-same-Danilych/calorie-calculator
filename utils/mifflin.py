"""
Расчёт базового обмена веществ (BMR) по формуле Миффлина-Сан Жеора,
суточного расхода калорий (TDEE) и целевых КБЖУ.
"""
from enum import Enum
from typing import Dict
from database.models import GoalType, ActivityLevel

# Множители активности для расчёта TDEE
ACTIVITY_MULTIPLIERS: Dict[ActivityLevel, float] = {
    ActivityLevel.SEDENTARY:   1.2,
    ActivityLevel.LIGHT:       1.375,
    ActivityLevel.MODERATE:    1.55,
    ActivityLevel.ACTIVE:      1.725,
    ActivityLevel.VERY_ACTIVE: 1.9,
}

# Корректировка калорий в зависимости от цели (дефицит/профицит)
GOAL_ADJUSTMENTS: Dict[GoalType, float] = {
    GoalType.LOSE: -500.0,
    GoalType.MAINTAIN:   0.0,
    GoalType.GAIN:    300.0,
}

# Безопасные минимальные границы калорий
MIN_CALORIES_FEMALE = 1200.0
MIN_CALORIES_MALE = 1500.0


def _validate_positive(value: float, name: str) -> None:
    """Вспомогательная функция для проверки положительных значений."""
    if value <= 0:
        raise ValueError(f"{name} должен быть больше 0. Получено: {value}")


def calculate_bmr(gender: str, weight_kg: float,
                  height_cm: float, age: int) -> float:
    """
    Базовый обмен веществ (BMR) по формуле Миффлина-Сан Жеора.

    Args:
        gender: "male" или "female"
        weight_kg: вес в кг (должен быть > 0)
        height_cm: рост в см (должен быть > 0)
        age: возраст в годах (должен быть > 0)

    Returns:
        BMR в ккал/сутки

    Raises:
        ValueError: если передан некорректный пол или отрицательные значения
    """
    # Валидация
    _validate_positive(weight_kg, "Вес")
    _validate_positive(height_cm, "Рост")
    if age <= 0:
        raise ValueError(f"Возраст должен быть больше 0. Получено: {age}")

    gender_lower = gender.lower()
    if gender_lower == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    elif gender_lower == "female":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        raise ValueError(
            f"Пол должен быть 'male' или 'female'. Получено: {gender}")


def calculate_tdee(
    gender: str,
    weight_kg: float,
    height_cm: float,
    age: int,
    activity: ActivityLevel
) -> float:
    """
    Суточный расход калорий (TDEE) с учётом физической активности.

    Returns:
        TDEE в ккал/сутки (округлённое до 1 знака)
    """
    bmr = calculate_bmr(gender, weight_kg, height_cm, age)
    return round(bmr * ACTIVITY_MULTIPLIERS[activity], 1)


def _ensure_min_calories(calories: float, gender: str) -> float:
    """
    Возвращает калории не ниже безопасного минимума для данного пола.
    """
    min_cal = MIN_CALORIES_MALE if gender == "male" else MIN_CALORIES_FEMALE
    return max(calories, min_cal)


def _calculate_protein_goal(weight_kg: float, goal: GoalType) -> float:
    """Белки: 1.6-2.0 г/кг в зависимости от цели."""
    protein_per_kg = {
        GoalType.LOSE:     1.8,
        GoalType.MAINTAIN: 1.6,
        GoalType.GAIN:     2.0,
    }[goal]
    return round(weight_kg * protein_per_kg, 1)


def _calculate_fat_goal(calories: float) -> float:
    """Жиры: 28% от калорий (9 ккал/г)."""
    return round(calories * 0.28 / 9, 1)


def _calculate_carbs_goal(calories: float,
                          protein: float, fat: float) -> float:
    """Углеводы: остаток калорий после белков и жиров (4 ккал/г)."""
    carbs = (calories - protein * 4 - fat * 9) / 4
    return max(0.0, round(carbs, 1))


def calculate_goals(
    gender: str,
    weight_kg: float,
    height_cm: float,
    age: int,
    activity: ActivityLevel,
    goal: GoalType
) -> Dict[str, float]:
    """
    Рассчитывает целевые КБЖУ на день на основе данных пользователя и его цели.

    Returns:
        Словарь с ключами:
            - calorie_goal: целевые калории (ккал/сутки)
            - protein_goal: целевые белки (г)
            - fat_goal: целевые жиры (г)
            - carb_goal: целевые углеводы (г)
    """
    tdee = calculate_tdee(gender, weight_kg, height_cm, age, activity)
    calories = tdee + GOAL_ADJUSTMENTS[goal]
    calories = round(_ensure_min_calories(calories, gender), 1)

    protein = _calculate_protein_goal(weight_kg, goal)
    fat = _calculate_fat_goal(calories)
    carbs = _calculate_carbs_goal(calories, protein, fat)

    return {
        "calorie_goal": calories,
        "protein_goal": protein,
        "fat_goal": fat,
        "carb_goal": carbs,
    }
