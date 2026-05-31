from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()


class GoalType(str, enum.Enum):
    LOSE = "lose"
    MAINTAIN = "maintain"
    GAIN = "gain"


class ActivityLevel(str, enum.Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    gender = Column(String(10), nullable=False)
    years = Column(Integer, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    activity = Column(String(20), nullable=False,
                      default=ActivityLevel.MODERATE)
    goal = Column(String(20), nullable=False, default=GoalType.MAINTAIN)

    calorie_goal = Column(Float, nullable=False, default=2000)
    protein_goal = Column(Float, nullable=False, default=150)
    fat_goal = Column(Float, nullable=False, default=67)
    carb_goal = Column(Float, nullable=False, default=250)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    diary_entries = relationship("DiaryEntry", back_populates="user",
                                 cascade="all, delete-orphan")


class FoodItem(Base):

    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    name_lower = Column(String(255), nullable=False,
                        index=True)

    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False, default=0.0)
    fat = Column(Float, nullable=False, default=0.0)
    carbs = Column(Float, nullable=False, default=0.0)

    barcode = Column(String(50), nullable=True,
                     index=True)
    is_custom = Column(Boolean, default=False)
    source = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)

    grams = Column(Float, nullable=False)
    meal_type = Column(String(20), nullable=False)
    eaten_at = Column(DateTime, default=datetime.utcnow)

    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)

    user = relationship("User", back_populates="diary_entries")
    food_item = relationship("FoodItem")
