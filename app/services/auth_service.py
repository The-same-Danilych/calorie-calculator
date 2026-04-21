from sqlalchemy.orm import Session
from app.models.user import User, SexEnum, GoalEnum
from app.schemas.user import UserCreate
from app.utils.security import hash_password, verify_password, create_access_token
from datetime import timedelta
from app.database.config import config
from datetime import datetime, timezone


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, user_data: UserCreate) -> User:
        existing_user = self.db.query(User).filter(
            User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Пользователь с таким email уже существует")

        new_user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            age=user_data.age,
            weight_kg=user_data.weight_kg,
            height_cm=user_data.height_cm,
            sex=user_data.sex,
            activity_factor=user_data.activity_factor,
            goal=user_data.goal
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user

    def login(self, email: str, password: str) -> dict:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("Неверный email или пароль")

        if not verify_password(password, user.password_hash):
            raise ValueError("Неверный email или пароль")
 
        user.last_login = datetime.now(timezone.utc)
        self.db.commit()

        access_token_expires = timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "user_id": user.id,
            "email": user.email,
            "daily_calorie_goal": user.calculate_daily_calories()
        }

    def get_user_by_id(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Пользователь не найден")
        return user

    def update_profile(self, user_id: int, **kwargs) -> User:
        user = self.get_user_by_id(user_id)

        allowed_fields = ['age', 'weight_kg',
                          'height_cm', 'activity_factor', 'goal']
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user
