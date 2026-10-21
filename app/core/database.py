import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Используем DATABASE_URL из окружения или локальный SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./tendermed.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency для внедрения сессии БД в FastAPI эндпоинты."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
