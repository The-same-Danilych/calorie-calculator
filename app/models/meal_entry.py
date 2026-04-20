from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base


class MealEntry(Base):
    __tablename__ = "meal_entries"

    id = Column(Integer, primary_key=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    quantity_grams = Column(Float, nullable=False)
    cached_calories = Column(Float, nullable=True)
    cached_protein = Column(Float, nullable=True)
    cached_fat = Column(Float, nullable=True)
    cached_carbs = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
