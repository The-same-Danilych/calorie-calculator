from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.food import Food
from app.schemas.food import FoodCreate
from typing import List

class FoodService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_food(self, food_data: FoodCreate, user_id: int = None) -> Food:
        food = Food(
            name=food_data.name,
            calories_per_100g=food_data.calories_per_100g,
            protein_per_100g=food_data.protein_per_100g,
            fat_per_100g=food_data.fat_per_100g,
            carbs_per_100g=food_data.carbs_per_100g,
            is_custom=True,
            created_by_user_id=user_id,
            source="user_added"
        )
        self.db.add(food)
        self.db.commit()
        self.db.refresh(food)
        return food
    
    def search_foods(self, query: str, limit: int = 20) -> List[Food]:
        search = f"%{query}%"
        foods = self.db.query(Food).filter(
            or_(
                Food.name.ilike(search),
                Food.name.ilike(f"{query}%")
            )
        ).order_by(
            Food.is_verified.desc(),
            Food.name
        ).limit(limit).all()
        return foods
    
    def get_food_by_id(self, food_id: int) -> Food:
        food = self.db.query(Food).filter(Food.id == food_id).first()
        if not food:
            raise ValueError("Продукт не найден")
        return food