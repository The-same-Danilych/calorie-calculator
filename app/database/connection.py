from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.database.config import config

DATABASE_URL = config.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=config.DEBUG,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = DeclarativeBase()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
