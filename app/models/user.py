from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Numeric
from sqlalchemy.sql import func
from app.database.connection import Base
import enum


class GoalEnum(str, enum.Enum):
    MAINTAIN = "maintain"
    LOSE = "lose"
    GAIN = "gain"


class SexEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    weight_kg = Column(Numeric(5, 2), nullable=False)
    height_cm = Column(Numeric(5, 2), nullable=False)
    sex = Column(Enum(SexEnum, name='sex_enum'), nullable=False)
    activity_factor = Column(Numeric(3, 2), nullable=False, default=1.2)
    goal = Column(Enum(GoalEnum, name='goal_enum'),
                  nullable=False, default=GoalEnum.MAINTAIN)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    last_login = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def calculate_daily_calories(self):
        if self.sex == SexEnum.MALE:
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age + 5
        else:
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age - 161

        tdee = bmr * self.activity_factor

        if self.goal == GoalEnum.LOSE:
            return tdee - 500
        elif self.goal == GoalEnum.GAIN:
            return tdee + 500
        return tdee
