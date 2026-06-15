import pytest
from api_clients.transactions_client import TransactionsClient
from api_clients.base_client import BaseClient

DATE_RANGE = "2026-06-08T00:00:00.000,2026-06-15T23:59:59.999"


def make_client(auth_client) -> TransactionsClient:
    token = auth_client.session.headers.get("Authorization", "").removeprefix("Bearer ")
    return TransactionsClient(token=token)


@pytest.fixture(scope="module")
def completed_payment(auth_client):
    """Возвращает dict с ключами id (внутренний) и tran_id (процессинговый)."""
    client = make_client(auth_client)
    response = client.get_transactions(
        created_range=DATE_RANGE,
        type_in="payment",
        size=50,
    )
    results = BaseClient.unwrap(response).get("results", [])
    for tx in results:
        if "Completed" in (tx.get("status_verbose") or "") or "CHARGED" in (tx.get("status_verbose") or ""):
            return {"id": tx["id"], "tran_id": tx["tran_id"], "cost": tx["cost"]}
    pytest.skip("No completed payment transaction found in date range")


@pytest.mark.api
class TestRefund:
    def test_refund_completed_payment(self, auth_client, completed_payment):
        client = make_client(auth_client)
        response = client.refund(completed_payment["id"], cost="1")
        # 200 — успешно, 400 — уже есть возврат или иная бизнес-ошибка
        assert response.status_code in (200, 400)
        assert response.json()["message"] in ("success", "error")

    def test_refund_invalid_cost(self, auth_client, completed_payment):
        client = make_client(auth_client)
        response = client.refund(completed_payment["id"], cost="999999999")
        assert response.status_code == 400

    def test_refund_missing_cost(self, auth_client, completed_payment):
        client = make_client(auth_client)
        response = client.session.post(
            f"{client._v1_url}/transactions/{completed_payment['id']}/refund/",
            json={},
        )
        assert response.status_code == 400

    def test_refund_nonexistent_transaction(self, auth_client):
        client = make_client(auth_client)
        response = client.refund(999999999, cost="1")
        assert response.status_code in (400, 404)


@pytest.mark.api
@pytest.mark.smoke
class TestSendWebhook:
    def test_send_webhook_success(self, auth_client, completed_payment):
        client = make_client(auth_client)
        response = client.send_webhook(completed_payment["tran_id"])
        assert response.status_code == 200
        assert response.json()["message"] == "success"
        assert "details" in BaseClient.unwrap(response)

    def test_send_webhook_nonexistent_transaction(self, auth_client):
        client = make_client(auth_client)
        response = client.send_webhook(999999999)
        assert response.status_code in (400, 404)


@pytest.mark.api
@pytest.mark.smoke
class TestRequestStatus:
    def test_request_status_success(self, auth_client, completed_payment):
        client = make_client(auth_client)
        response = client.request_status(completed_payment["tran_id"])
        assert response.status_code == 200
        assert response.json()["message"] == "success"
        assert "details" in BaseClient.unwrap(response)

    def test_request_status_nonexistent_transaction(self, auth_client):
        client = make_client(auth_client)
        response = client.request_status(999999999)
        assert response.status_code in (400, 404)
