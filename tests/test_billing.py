import pytest
from tests.test_api import client


def test_get_billing_plans():
    resp = client.get("/api/billing/plans")
    assert resp.status_code == 200
    plans = resp.json()
    assert len(plans) == 3
    plan_ids = [p["id"] for p in plans]
    assert "start" in plan_ids
    assert "pro" in plan_ids
    assert "corp" in plan_ids


def test_billing_checkout_and_transactions():
    # 1. Регистрация тестового пользователя
    reg_resp = client.post("/api/auth/register", json={
        "email": "buyer@yandex.ru",
        "password": "strongpassword123",
        "company_name": "ООО МедСнаб",
    })
    assert reg_resp.status_code == 200
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Изначально 3 кредита
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.json()["available_credits"] == 3

    # 2. Покупка тарифа "pro" (+50 кредитов)
    checkout_resp = client.post(
        "/api/billing/checkout",
        json={"plan_id": "pro", "payment_method": "card"},
        headers=headers,
    )
    assert checkout_resp.status_code == 200
    data = checkout_resp.json()
    assert data["success"] is True
    assert data["credits_added"] == 50
    assert data["new_credits_balance"] == 53

    # 3. Проверка обновленного баланса в /me
    me_resp2 = client.get("/api/auth/me", headers=headers)
    assert me_resp2.json()["available_credits"] == 53

    # 4. Проверка истории транзакций
    tx_resp = client.get("/api/billing/transactions", headers=headers)
    assert tx_resp.status_code == 200
    txs = tx_resp.json()
    assert len(txs) == 1
    assert txs[0]["plan_id"] == "pro"
    assert txs[0]["amount_rubles"] == 5900
    assert txs[0]["credits_added"] == 50
