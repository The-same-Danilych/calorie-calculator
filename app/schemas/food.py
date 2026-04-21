from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class FoodBase(BaseModel):
    name: str
    calories_per_100g: float
    protein_per_100g: float = 0
    fat_per_100g: float = 0
    carbs_per_100g: float = 0


class FoodCreate(FoodBase):
    pass


class FoodResponse(FoodBase):
    id: int
    is_custom: bool
    created_by_user_id: Optional[int]
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FoodSearchResponse(BaseModel):
    id: int
    name: str
    calories_per_100g: float
    protein_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float

    model_config = ConfigDict(from_attributes=True)
