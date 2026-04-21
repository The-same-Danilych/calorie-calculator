from sqlalchemy.orm import Session
from app.models.meal import Meal
from app.models.meal_entry import MealEntry
from app.models.food import Food
from app.schemas.meal import MealCreate
from typing import List
from datetime import date


class MealService:
    def __init__(self, db: Session):
        self.db = db

    def create_meal(self, user_id: int, meal_data: MealCreate) -> Meal:
        meal = Meal(
            user_id=user_id,
            meal_type=meal_data.meal_type,
            eaten_at=meal_data.eaten_at,
            notes=meal_data.notes
        )
        self.db.add(meal)
        self.db.flush()

        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0

        for entry_data in meal_data.entries:
            food = self.db.query(Food).filter(
                Food.id == entry_data.food_id).first()
            if not food:
                raise ValueError(
                    f"Продукт с ID {entry_data.food_id} не найден")

            quantity = entry_data.quantity_grams
            calories = (food.calories_per_100g * quantity) / 100
            protein = (food.protein_per_100g * quantity) / 100
            fat = (food.fat_per_100g * quantity) / 100
            carbs = (food.carbs_per_100g * quantity) / 100

            total_calories += calories
            total_protein += protein
            total_fat += fat
            total_carbs += carbs

            entry = MealEntry(
                meal_id=meal.id,
                food_id=food.id,
                quantity_grams=quantity,
                cached_calories=calories,
                cached_protein=protein,
                cached_fat=fat,
                cached_carbs=carbs
            )
            self.db.add(entry)

        self.db.commit()
        self.db.refresh(meal)

        meal.total_calories = total_calories
        meal.total_protein = total_protein
        meal.total_fat = total_fat
        meal.total_carbs = total_carbs

        return meal

    def get_user_meals(self, user_id: int, meal_date: date = None) -> List[Meal]:
        query = self.db.query(Meal).filter(Meal.user_id == user_id)

        if meal_date:
            query = query.filter(Meal.eaten_at.cast(date) == meal_date)

        meals = query.order_by(Meal.eaten_at.desc()).all()

        for meal in meals:
            entries = self.db.query(MealEntry).filter(
                MealEntry.meal_id == meal.id).all()
            meal.total_calories = sum(e.cached_calories or 0 for e in entries)
            meal.total_protein = sum(e.cached_protein or 0 for e in entries)
            meal.total_fat = sum(e.cached_fat or 0 for e in entries)
            meal.total_carbs = sum(e.cached_carbs or 0 for e in entries)
            meal.entries = entries

            for entry in entries:
                food = self.db.query(Food).filter(
                    Food.id == entry.food_id).first()
                entry.food_name = food.name if food else "Неизвестный продукт"

        return meals

    def get_meal_entries(self, meal_id: int) -> List[MealEntry]:
        entries = self.db.query(MealEntry).filter(
            MealEntry.meal_id == meal_id).all()
        for entry in entries:
            food = self.db.query(Food).filter(Food.id == entry.food_id).first()
            entry.food_name = food.name if food else "Неизвестный продукт"
            entry.calories = entry.cached_calories or 0
            entry.protein = entry.cached_protein or 0
            entry.fat = entry.cached_fat or 0
            entry.carbs = entry.cached_carbs or 0
        return entries
