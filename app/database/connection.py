from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.database.config import config

DATABASE_URL = config.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=config.DEBUG,
    pool_size=5,
    max_overflow=10,
    connect_args={"options": "-c search_path=core,public"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Base.metadata.schema = "core"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
