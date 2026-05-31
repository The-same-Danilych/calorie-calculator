from database.models import GoalType, ActivityLevel

ACTIVITY_MULTIPLIERS = {
    ActivityLevel.SEDENTARY:   1.2,
    ActivityLevel.LIGHT:       1.375,
    ActivityLevel.MODERATE:    1.55,
    ActivityLevel.ACTIVE:      1.725,
    ActivityLevel.VERY_ACTIVE: 1.9,
}

GOAL_ADJUSTMENTS = {
    GoalType.LOSE: -500,
    GoalType.MAINTAIN: 0,
    GoalType.GAIN: +300,
}


def calculate_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
    """Базовый обмен веществ по формуле Миффлина-Сан Жеора.

    Аргументы:
        gender: "male" или "female"
        weight_kg: вес в кг
        height_cm: рост в см
        age: возраст в годах (полных лет)
    """
    if gender == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calculate_tdee(gender: str, weight_kg: float, height_cm: float,
                   age: int, activity: ActivityLevel) -> float:
    """Суточный расход калорий с учётом активности."""
    bmr = calculate_bmr(gender, weight_kg, height_cm, age)
    return round(bmr * ACTIVITY_MULTIPLIERS[activity], 1)


def calculate_goals(gender: str, weight_kg: float, height_cm: float,
                    age: int, activity: ActivityLevel,
                    goal: GoalType) -> dict:
    """Рассчитывает целевые КБЖУ на день.

    Аргументы:
        gender: "male" или "female"
        weight_kg: вес в кг
        height_cm: рост в см
        age: возраст в годах (полных лет)
        activity: уровень активности
        goal: цель (сброс/поддержание/набор)
    """
    tdee = calculate_tdee(gender, weight_kg, height_cm, age, activity)
    calories = round(tdee + GOAL_ADJUSTMENTS[goal], 1)

    # Минимум 1200 ккал для женщин и 1500 для мужчин — безопасный минимум
    min_calories = 1500 if gender == "male" else 1200
    calories = max(calories, float(min_calories))

    protein_per_kg = {
        GoalType.LOSE:     1.8,
        GoalType.MAINTAIN: 1.6,
        GoalType.GAIN:     2.0,
    }[goal]

    protein = round(weight_kg * protein_per_kg, 1)
    fat = round(calories * 0.28 / 9, 1)
    carbs = round((calories - protein * 4 - fat * 9) / 4, 1)

    return {
        "calorie_goal": calories,
        "protein_goal": protein,
        "fat_goal":     fat,
        "carb_goal":    max(carbs, 0.0),
    }
