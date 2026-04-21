from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class MealEntryCreate(BaseModel):
    food_id: int
    quantity_grams: float


class MealEntryResponse(BaseModel):
    id: int
    food_id: int
    food_name: str
    quantity_grams: float
    calories: float
    protein: float
    fat: float
    carbs: float

    model_config = ConfigDict(from_attributes=True)


class MealCreate(BaseModel):
    meal_type: str
    eaten_at: datetime
    notes: Optional[str] = None
    entries: List[MealEntryCreate]


class MealResponse(BaseModel):
    id: int
    meal_type: str
    eaten_at: datetime
    notes: Optional[str]
    total_calories: float
    total_protein: float
    total_fat: float
    total_carbs: float
    entries: List[MealEntryResponse]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailySummaryResponse(BaseModel):
    date: str
    total_calories: float
    total_protein: float
    total_fat: float
    total_carbs: float
    target_calories: float
    percentage: float

    model_config = ConfigDict(from_attributes=True)
