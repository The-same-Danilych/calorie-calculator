from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.schemas.food import FoodCreate, FoodResponse, FoodSearchResponse
from app.services.food_service import FoodService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/foods", tags=["Продукты"])


@router.post("/", response_model=FoodResponse)
async def create_food(
    food_data: FoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    food_service = FoodService(db)
    food = food_service.create_food(food_data, current_user.id)
    return food


@router.get("/search", response_model=List[FoodSearchResponse])
async def search_foods(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    food_service = FoodService(db)
    foods = food_service.search_foods(q, limit)
    return foods


@router.get("/{food_id}", response_model=FoodResponse)
async def get_food(
    food_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    food_service = FoodService(db)
    try:
        food = food_service.get_food_by_id(food_id)
        return food
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
