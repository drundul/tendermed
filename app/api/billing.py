"""
Billing & Plans API — Модуль монетизации и тарифов SaaS TenderMed.
Предоставляет тарифную сетку, пополнение баланса проверок и историю транзакций.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import User, PaymentTransaction
from app.api.auth import get_current_user
from app.models.schemas import (
    BillingPlan,
    CreatePaymentRequest,
    PaymentSuccessResponse,
    PaymentTransactionResponse,
)

router = APIRouter(prefix="/api/billing", tags=["billing"])

# Официальная тарифная сетка TenderMed
PLANS = [
    BillingPlan(
        id="start",
        name="Старт",
        tagline="Для небольших поставщиков и периодического участия в торгах",
        price_rubles=1900,
        credits_count=15,
        price_per_audit="126 ₽ / аудит",
        badge="Базовый",
        popular=False,
        features=[
            "15 полных проверок документации",
            "Автономный аудит 44-ФЗ и ИИ-анализ",
            "Выявление рисков ПП РФ № 878 и РУ Росздравнадзора",
            "Экспорт экспертных заключений в Word (.docx)",
            "Подготовка запросов на разъяснение положений",
            "Срок действия пакета: бессрочно",
        ],
    ),
    BillingPlan(
        id="pro",
        name="Профи / Медтехника",
        tagline="Оптимально для активных участников медицинских аукционов",
        price_rubles=5900,
        credits_count=50,
        price_per_audit="118 ₽ / аудит",
        badge="Хит продаж • Рекомендуем",
        popular=True,
        features=[
            "50 полных аудитов закупок",
            "Все возможности тарифа Старт",
            "⚖️ Конструктор официальной Жалобы в ФАС (ст. 105 44-ФЗ)",
            "Скачивание готовых жалоб в Word для подачи через ЕИС",
            "Глубокий инженерный поиск скрытых заточек ТЗ (DF4, патенты)",
            "Аудит незаконных условий сроков поставки (режим 24 часа)",
            "Проверка формул неустоек и штрафов по ПП РФ № 1042",
        ],
    ),
    BillingPlan(
        id="corp",
        name="Корпоративный",
        tagline="Для тендерных отделов, дистрибьюторов и производителей",
        price_rubles=14900,
        credits_count=150,
        price_per_audit="99 ₽ / аудит",
        badge="Максимум выгоды",
        popular=False,
        features=[
            "150 проверок документации (самая выгодная цена за аудит)",
            "Все возможности тарифа Профи",
            "Генератор жалоб в территориальные УФАС без ограничений",
            "Многопользовательский доступ для сотрудников компании",
            "Приоритетная очередь анализа (до 5 секунд)",
            "Поддержка загрузки архивов и таблиц Excel (.xlsx)",
            "Персональная линия консультаций эксперта 44-ФЗ",
        ],
    ),
]


@router.get("/plans", response_model=List[BillingPlan])
def get_plans():
    """Получение актуальной тарифной сетки."""
    return PLANS


@router.post("/checkout", response_model=PaymentSuccessResponse)
def checkout_plan(
    payload: CreatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Пополнение баланса проверок пользователя.
    В текущей версии эмулирует успешное подтверждение через эквайринг (ЮKassa / CloudPayments),
    мгновенно начисляет кредиты и логирует транзакцию в БД.
    """
    plan = next((p for p in PLANS if p.id == payload.plan_id), None)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тарифный план '{payload.plan_id}' не найден",
        )

    # 1. Начисляем проверки пользователю
    current_user.available_credits += plan.credits_count

    # 2. Фиксируем транзакцию
    tx = PaymentTransaction(
        user_id=current_user.id,
        plan_id=plan.id,
        plan_name=plan.name,
        amount_rubles=plan.price_rubles,
        credits_added=plan.credits_count,
        status="completed",
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    db.refresh(current_user)

    return PaymentSuccessResponse(
        success=True,
        transaction_id=tx.id,
        plan_name=plan.name,
        credits_added=plan.credits_count,
        new_credits_balance=current_user.available_credits,
        message=f"Тариф «{plan.name}» успешно активирован! Начислено {plan.credits_count} проверок.",
    )


@router.get("/transactions", response_model=List[PaymentTransactionResponse])
def get_user_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """История покупок и пополнений баланса пользователя."""
    txs = (
        db.query(PaymentTransaction)
        .filter(PaymentTransaction.user_id == current_user.id)
        .order_by(PaymentTransaction.created_at.desc())
        .all()
    )
    return [
        PaymentTransactionResponse(
            id=t.id,
            plan_id=t.plan_id,
            plan_name=t.plan_name,
            amount_rubles=t.amount_rubles,
            credits_added=t.credits_added,
            status=t.status,
            created_at=t.created_at.strftime("%d.%m.%Y %H:%M") if t.created_at else "",
        )
        for t in txs
    ]
