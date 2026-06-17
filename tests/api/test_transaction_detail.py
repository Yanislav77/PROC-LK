"""API-тесты: детальная информация транзакции v4, история статусов v1."""
import pytest
from api_clients.transactions_client import TransactionsClient
from api_clients.base_client import BaseClient

DATE_RANGE = "2026-01-01T00:00:00.000,2026-06-17T23:59:59.999"

DETAIL_BASE_FIELDS = [
    "order_id", "tran_id", "created", "service_id", "service_name",
    "status_id", "status_verbose", "cost", "currency",
]

DETAIL_EXTENDED_FIELDS = [
    "amount_total_fee_internal", "payment_method", "is_test",
    "masked_pan", "cardholder", "email", "phone_number",
]

HISTORY_FIELDS = [
    "history_id", "created", "service_id", "service_name",
    "status_id", "status_verbose", "cost", "currency",
    "masked_pan", "cardholder", "tran_id", "error_code",
]


def make_client(auth_client) -> TransactionsClient:
    token = auth_client.session.headers.get("Authorization", "").removeprefix("Bearer ")
    return TransactionsClient(token=token)


@pytest.fixture(scope="module")
def transaction_id(auth_client):
    """Возвращает внутренний id первой доступной транзакции из списка."""
    client = make_client(auth_client)
    response = client.get_transactions(created_range=DATE_RANGE, size=5)
    results = BaseClient.unwrap(response).get("results", [])
    if not results:
        pytest.skip("No transactions available for detail tests")
    return results[0]["id"]


@pytest.mark.api
class TestTransactionDetailV4:
    """GET /api/v4/transactions/{transaction_id}/ — новый эндпоинт детализации."""

    @pytest.fixture(autouse=True)
    def setup(self, auth_client):
        self.client = make_client(auth_client)

    def test_returns_200(self, transaction_id):
        """Эндпоинт возвращает статус 200."""
        response = self.client.get_transaction_detail(transaction_id)
        assert response.status_code == 200

    def test_base_fields_present(self, transaction_id):
        """Базовые поля, совместимые с v1 list, присутствуют в ответе."""
        data = BaseClient.unwrap(self.client.get_transaction_detail(transaction_id))
        missing = [f for f in DETAIL_BASE_FIELDS if f not in data]
        assert not missing, f"Missing base fields: {missing}"

    def test_extended_fields_present(self, transaction_id):
        """Новые поля, необходимые для страницы детализации, присутствуют."""
        data = BaseClient.unwrap(self.client.get_transaction_detail(transaction_id))
        missing = [f for f in DETAIL_EXTENDED_FIELDS if f not in data]
        assert not missing, f"Missing extended fields: {missing}"

    def test_p2p_bankdetails_present(self, transaction_id):
        """Объект p2p_bankdetails присутствует в ответе."""
        data = BaseClient.unwrap(self.client.get_transaction_detail(transaction_id))
        assert "p2p_bankdetails" in data

    def test_p2p_bankdetails_has_required_keys(self, transaction_id):
        """p2p_bankdetails содержит ключи accountNumber и phoneNumber."""
        data = BaseClient.unwrap(self.client.get_transaction_detail(transaction_id))
        bankdetails = data.get("p2p_bankdetails", {})
        assert "accountNumber" in bankdetails
        assert "phoneNumber" in bankdetails

    def test_p2p_bankdetails_mutual_exclusive(self, transaction_id):
        """accountNumber и phoneNumber не могут быть заполнены одновременно."""
        data = BaseClient.unwrap(self.client.get_transaction_detail(transaction_id))
        bankdetails = data.get("p2p_bankdetails", {})
        account = bankdetails.get("accountNumber") or ""
        phone = bankdetails.get("phoneNumber") or ""
        assert not (account and phone), (
            f"Both accountNumber='{account}' and phoneNumber='{phone}' are non-empty"
        )

    def test_returns_404_for_unknown_id(self):
        """Несуществующий transaction_id возвращает 404."""
        response = self.client.get_transaction_detail(999999999)
        assert response.status_code == 404


@pytest.mark.api
class TestTransactionHistoryV1:
    """GET /api/v1/transactions/{transaction_id}/history/ — история статусов."""

    @pytest.fixture(autouse=True)
    def setup(self, auth_client):
        self.client = make_client(auth_client)

    def test_returns_200(self, transaction_id):
        """Эндпоинт возвращает статус 200."""
        response = self.client.get_transaction_history(transaction_id)
        assert response.status_code == 200

    def test_response_has_pagination_structure(self, transaction_id):
        """Ответ содержит пагинационные ключи: count, next, previous, results."""
        data = BaseClient.unwrap(self.client.get_transaction_history(transaction_id))
        for key in ("count", "next", "previous", "results"):
            assert key in data, f"Missing pagination key: {key}"

    def test_history_result_fields_present(self, transaction_id):
        """Каждый элемент истории содержит все обязательные поля."""
        data = BaseClient.unwrap(self.client.get_transaction_history(transaction_id))
        results = data.get("results", [])
        if not results:
            pytest.skip("Transaction has no history records")
        missing = [f for f in HISTORY_FIELDS if f not in results[0]]
        assert not missing, f"Missing history fields: {missing}"

    def test_history_sorted_by_created_desc(self, transaction_id):
        """История отсортирована по дате создания: новые записи сверху (DESC)."""
        data = BaseClient.unwrap(self.client.get_transaction_history(transaction_id))
        results = data.get("results", [])
        if len(results) < 2:
            pytest.skip("Not enough history records to verify sort order")
        dates = [r["created"] for r in results]
        assert dates == sorted(dates, reverse=True), (
            f"History not sorted DESC. Got: {dates[:3]}"
        )

    def test_returns_404_for_unknown_id(self):
        """Несуществующий transaction_id возвращает 404."""
        response = self.client.get_transaction_history(999999999)
        assert response.status_code == 404
