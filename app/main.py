import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Обеспечиваем корректный sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.core.database import engine, Base
from app.db import models  # noqa: F401 - регистрируем модели для SQLAlchemy
from app.api.auth import router as auth_router
from app.api.tenders import router as tenders_router
from app.api.exports import router as exports_router
from app.api.billing import router as billing_router

# Создание таблиц БД при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TenderMed API",
    description="SaaS API для экспертного ИИ-аудита тендерной документации на поставку сложной медтехники",
    version="2.0.0",
)

# Настройка CORS для работы с Next.js фронтендом (локально и на боевом домене)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://tendermed.ru",
        "https://www.tendermed.ru",
        "*",  # для гибкости в dev-режиме
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth_router)
app.include_router(tenders_router)
app.include_router(exports_router)
app.include_router(billing_router)


@app.get("/api/health")
def health_check():
    """Проверка доступности API."""
    return {"status": "ok", "service": "TenderMed API", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
