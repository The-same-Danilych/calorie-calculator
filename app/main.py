from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, foods, meals
from app.database.connection import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Calorie Counter API",
    description="API для мобильного приложения счётчика калорий",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(foods.router)
app.include_router(meals.router)


@app.get("/")
async def root():
    return {
        "message": "Calorie Counter API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
