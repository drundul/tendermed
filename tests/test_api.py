import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.schemas import (
    FullAnalysisReport,
    TenderSummary,
    MedComplianceAudit,
    TrafficLightVerdict,
    ClarificationRequest,
)
from app.db.models import TenderAudit, User

# Тестовая БД SQLite в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_auth_register_and_login():
    # 1. Регистрация
    reg_payload = {
        "email": "doctor@medtech-supplier.ru",
        "password": "secretpassword123",
        "company_name": "ООО МедТехПоставка",
    }
    reg_resp = client.post("/api/auth/register", json=reg_payload)
    assert reg_resp.status_code == 200
    data = reg_resp.json()
    assert "access_token" in data
    assert data["available_credits"] == 3  # 3 бесплатных аудита
    assert data["email"] == "doctor@medtech-supplier.ru"

    token = data["access_token"]

    # 2. Повторная регистрация с тем же email -> ошибка 400
    dup_resp = client.post("/api/auth/register", json=reg_payload)
    assert dup_resp.status_code == 400

    # 3. Вход
    login_resp = client.post("/api/auth/login", json={
        "email": "doctor@medtech-supplier.ru",
        "password": "secretpassword123",
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    # 4. Проверка /me
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "doctor@medtech-supplier.ru"
    assert me_data["available_credits"] == 3


def test_unauthorized_access():
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_audit_history_and_export():
    # Регистрируем пользователя
    reg_resp = client.post("/api/auth/register", json={
        "email": "test@tender.ru",
        "password": "testpassword",
    })
    token = reg_resp.json()["access_token"]

    # Создаем фиктивный отчет в БД напрямую
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "test@tender.ru").first()

    mock_report = FullAnalysisReport(
        verdict=TrafficLightVerdict.RED,
        risk_score=85,
        verdict_summary="Выявлены риски штрафов",
        summary=TenderSummary(
            purchase_subject="Поставка УЗИ аппарата",
            notice_number="0142200001326018834",
            customer_name="ГБУЗ Самарская ОКБ",
        ),
        med_compliance=MedComplianceAudit(
            ru_required=True,
            ru_notes="Требуется РУ",
            national_regime_applies=True,
            national_regime_details="ПП 878",
        ),
        clarification_requests=[
            ClarificationRequest(
                subject="О снижении штрафа",
                justification="ПП 1042",
                draft_text="Просим снизить штраф...",
            )
        ],
    )

    audit = TenderAudit(
        user_id=user.id,
        notice_number="0142200001326018834",
        purchase_subject="Поставка УЗИ аппарата",
        customer_name="ГБУЗ Самарская ОКБ",
        law_type="44-ФЗ",
        verdict="RED",
        risk_score=85,
        report_json=mock_report.model_dump_json(),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    audit_id = audit.id
    db.close()

    # 1. Запрос истории
    hist_resp = client.get("/api/tenders/history", headers={"Authorization": f"Bearer {token}"})
    assert hist_resp.status_code == 200
    audits = hist_resp.json()
    assert len(audits) == 1
    assert audits[0]["notice_number"] == "0142200001326018834"

    # 2. Экспорт отчета в DOCX
    docx_resp = client.get(f"/api/exports/tenders/{audit_id}/report.docx", headers={"Authorization": f"Bearer {token}"})
    assert docx_resp.status_code == 200
    assert docx_resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert len(docx_resp.content) > 0

    # 3. Экспорт запроса в DOCX
    cr_resp = client.get(f"/api/exports/tenders/{audit_id}/clarification/1.docx", headers={"Authorization": f"Bearer {token}"})
    assert cr_resp.status_code == 200
    assert len(cr_resp.content) > 0

    # 4. Экспорт всех запросов в DOCX
    all_cr_resp = client.get(f"/api/exports/tenders/{audit_id}/clarifications.docx", headers={"Authorization": f"Bearer {token}"})
    assert all_cr_resp.status_code == 200
    assert len(all_cr_resp.content) > 0
