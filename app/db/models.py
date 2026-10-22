from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """Пользователь системы TenderMed."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    
    # Кредиты на проверки (при регистрации выдается 3 бесплатных аудита)
    available_credits = Column(Integer, default=3, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    audits = relationship("TenderAudit", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("PaymentTransaction", back_populates="user", cascade="all, delete-orphan")


class PaymentTransaction(Base):
    """Транзакция пополнения баланса аудитов."""
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(String, nullable=False)
    plan_name = Column(String, nullable=False)
    amount_rubles = Column(Integer, nullable=False)
    credits_added = Column(Integer, nullable=False)
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="payments")


class TenderAudit(Base):
    """История проверок закупок пользователем."""
    __tablename__ = "tender_audits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    source_url = Column(String, nullable=True)
    notice_number = Column(String, nullable=True, index=True)
    purchase_subject = Column(String, nullable=False)
    customer_name = Column(String, nullable=True)
    law_type = Column(String, default="44-ФЗ")
    
    # Вердикт и показатели
    verdict = Column(String, nullable=False)  # RED, YELLOW, GREEN
    risk_score = Column(Integer, nullable=False)  # 0..100
    execution_time_seconds = Column(String, nullable=True)
    
    # Сериализованный JSON полного отчета FullAnalysisReport
    report_json = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="audits")
