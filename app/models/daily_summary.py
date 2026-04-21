from sqlalchemy import Column, Integer, ForeignKey, Numeric, Date, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base


class DailySummary(Base):
    __tablename__ = "daily_summaries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)

    # Типы Numeric, а не Float
    total_calories = Column(Numeric(8, 2), default=0)
    total_protein = Column(Numeric(8, 2), default=0)
    total_fat = Column(Numeric(8, 2), default=0)
    total_carbs = Column(Numeric(8, 2), default=0)
    target_calories = Column(Numeric(8, 2), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
