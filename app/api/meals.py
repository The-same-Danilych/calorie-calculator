from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database.connection import get_db
from app.schemas.meal import MealCreate, MealResponse, DailySummaryResponse
from app.services.meal_service import MealService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.daily_summary import DailySummary

router = APIRouter(prefix="/meals", tags=["Приёмы пищи"])


@router.post("/", response_model=MealResponse)
async def create_meal(
    meal_data: MealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meal_service = MealService(db)
    try:
        meal = meal_service.create_meal(current_user.id, meal_data)

        # Формируем ответ
        entries = meal_service.get_meal_entries(meal.id)

        return MealResponse(
            id=meal.id,
            meal_type=meal.meal_type,
            eaten_at=meal.eaten_at,
            notes=meal.notes,
            total_calories=getattr(meal, 'total_calories', 0),
            total_protein=getattr(meal, 'total_protein', 0),
            total_fat=getattr(meal, 'total_fat', 0),
            total_carbs=getattr(meal, 'total_carbs', 0),
            entries=[
                {
                    "id": e.id,
                    "food_id": e.food_id,
                    "food_name": getattr(e, 'food_name', ''),
                    "quantity_grams": e.quantity_grams,
                    "calories": getattr(e, 'calories', 0),
                    "protein": getattr(e, 'protein', 0),
                    "fat": getattr(e, 'fat', 0),
                    "carbs": getattr(e, 'carbs', 0)
                }
                for e in entries
            ],
            created_at=meal.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[MealResponse])
async def get_meals(
    meal_date: Optional[date] = Query(
        None, description="Дата в формате YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meal_service = MealService(db)
    meals = meal_service.get_user_meals(current_user.id, meal_date)

    response = []
    for meal in meals:
        response.append(MealResponse(
            id=meal.id,
            meal_type=meal.meal_type,
            eaten_at=meal.eaten_at,
            notes=meal.notes,
            total_calories=getattr(meal, 'total_calories', 0),
            total_protein=getattr(meal, 'total_protein', 0),
            total_fat=getattr(meal, 'total_fat', 0),
            total_carbs=getattr(meal, 'total_carbs', 0),
            entries=[
                {
                    "id": e.id,
                    "food_id": e.food_id,
                    "food_name": getattr(e, 'food_name', ''),
                    "quantity_grams": e.quantity_grams,
                    "calories": getattr(e, 'calories', 0),
                    "protein": getattr(e, 'protein', 0),
                    "fat": getattr(e, 'fat', 0),
                    "carbs": getattr(e, 'carbs', 0)
                }
                for e in getattr(meal, 'entries', [])
            ],
            created_at=meal.created_at
        ))

    return response


@router.get("/summary/{summary_date}", response_model=DailySummaryResponse)
async def get_daily_summary(
    summary_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    summary = db.query(DailySummary).filter(
        DailySummary.user_id == current_user.id,
        DailySummary.date == summary_date
    ).first()

    if not summary:
        return DailySummaryResponse(
            date=str(summary_date),
            total_calories=0,
            total_protein=0,
            total_fat=0,
            total_carbs=0,
            target_calories=current_user.calculate_daily_calories(),
            percentage=0
        )

    percentage = (float(summary.total_calories) /
                  float(summary.target_calories) * 100) if summary.target_calories else 0

    return DailySummaryResponse(
        date=str(summary.date),
        total_calories=float(summary.total_calories),
        total_protein=float(summary.total_protein),
        total_fat=float(summary.total_fat),
        total_carbs=float(summary.total_carbs),
        target_calories=float(
            summary.target_calories) if summary.target_calories else current_user.calculate_daily_calories(),
        percentage=round(percentage, 1)
    )
