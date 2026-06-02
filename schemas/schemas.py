"""Pydantic‑схемы для валидации данных, поступающих от пользователя."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from database.models import GoalType, ActivityLevel


class UserCreate(BaseModel):
    """Схема для создания/обновления пользователя."""
    name:       str = Field(..., min_length=1, max_length=100)
    gender:     str = Field(..., pattern="^(male|female)$")
    years:      int = Field(..., ge=15, le=120)
    height_cm:  float = Field(..., ge=50, le=300)
    weight_kg:  float = Field(..., ge=20, le=500)
    activity:   ActivityLevel = ActivityLevel.MODERATE
    goal:       GoalType = GoalType.MAINTAIN

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        return v.strip()


class FoodItemCreate(BaseModel):
    """Схема для добавления продукта."""
    name:      str = Field(..., min_length=1, max_length=255)
    calories:  float = Field(..., ge=0, le=9000)
    protein:   float = Field(default=0.0, ge=0, le=100)
    fat:       float = Field(default=0.0, ge=0, le=100)
    carbs:     float = Field(default=0.0, ge=0, le=100)
    is_custom: bool = False

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        return v.strip().capitalize()

    @field_validator("calories", "protein", "fat", "carbs", mode="before")
    @classmethod
    def round_two(cls, v):
        if v is None:
            return 0.0
        try:
            return max(0.0, round(float(v), 2))
        except (TypeError, ValueError):
            return 0.0


class DiaryEntryCreate(BaseModel):
    """Схема для добавления записи в дневник."""
    food_item_id: int
    grams:        float = Field(..., gt=0, le=5000)
    meal_type:    str = Field(..., pattern="^(breakfast|lunch|dinner|snack)$")


class DiaryEntryUpdate(BaseModel):
    """Схема для обновления записи дневника."""
    grams: Optional[float] = Field(None, gt=0, le=5000)
    meal_type: Optional[str] = Field(
        None, pattern="^(breakfast|lunch|dinner|snack)$")
    food_data: Optional[FoodItemCreate] = None
