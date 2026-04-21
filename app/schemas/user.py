from pydantic import ConfigDict, BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class SexEnum(str, Enum):
    male = "male"
    female = "female"


class GoalEnum(str, Enum):
    maintain = "maintain"
    lose = "lose"
    gain = "gain"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    age: int = Field(..., ge=10, le=120)
    weight_kg: float = Field(..., gt=0, lt=500)
    height_cm: float = Field(..., gt=0, lt=300)
    sex: SexEnum
    activity_factor: float = Field(..., ge=1.0, le=2.5)
    goal: GoalEnum = GoalEnum.maintain


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    daily_calorie_goal: float


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    age: int
    weight_kg: float
    height_cm: float
    sex: SexEnum
    activity_factor: float
    goal: GoalEnum
    daily_calorie_goal: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
