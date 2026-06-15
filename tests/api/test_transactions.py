import pytest
from api_clients.transactions_client import TransactionsClient
from api_clients.base_client import BaseClient


def make_client(auth_client) -> TransactionsClient:
    token = auth_client.session.headers.get("Authorization", "").removeprefix("Bearer ")
    return TransactionsClient(token=token)


@pytest.mark.api
class TestTransactionsList:
    def test_get_transactions_with_date_range(self, auth_client):
        client = make_client(auth_client)
        response = client.get_transactions(
            created_range="2026-06-08T00:00:00.000,2026-06-15T23:59:59.999",
            type_in="payment",
        )
        assert response.status_code == 200
        data = BaseClient.unwrap(response)
        assert "count" in data
        assert "results" in data

    def test_get_transactions_pagination(self, auth_client):
        client = make_client(auth_client)
        response = client.get_transactions(
            created_range="2026-06-08T00:00:00.000,2026-06-15T23:59:59.999",
            page=1,
            size=5,
        )
        assert response.status_code == 200
        data = BaseClient.unwrap(response)
        assert len(data.get("results", [])) <= 5

    def test_transaction_fields_present(self, auth_client):
        client = make_client(auth_client)
        response = client.get_transactions(
            created_range="2026-06-08T00:00:00.000,2026-06-15T23:59:59.999",
        )
        assert response.status_code == 200
        results = BaseClient.unwrap(response).get("results", [])
        if results:
            keys = results[0].keys()
            for field in ("id", "tran_id", "status_verbose", "cost", "currency", "type"):
                assert field in keys


@pytest.mark.api
class TestTransactionNewParams:
    @pytest.fixture(autouse=True)
    def setup(self, auth_client):
        self.client = make_client(auth_client)

    def test_filter_by_payment_method_card(self):
        response = self.client.get_transactions(
            created_range="2026-06-08T00:00:00.000,2026-06-15T23:59:59.999",
            payment_method="Card",
        )
        assert response.status_code == 200

    def test_filter_by_payment_method_p2p(self):
        response = self.client.get_transactions(
            created_range="2026-06-08T00:00:00.000,2026-06-15T23:59:59.999",
            payment_method="P2P",
        )
        assert response.status_code == 200

    def test_filter_by_payed_range(self):
        response = self.client.get_transactions(
            payed_range="2026-06-08T00:00:00.000,2026-06-15T23:59:59.999",
        )
        assert response.status_code == 200

    def test_filter_by_type_payout(self):
        response = self.client.get_transactions(
            created_range="2026-06-08T00:00:00.000,2026-06-15T23:59:59.999",
            type_in="payout",
        )
        assert response.status_code == 200

    def test_response_contains_p2p_bankdetails(self):
        response = self.client.get_transactions(
            created_range="2026-06-08T00:00:00.000,2026-06-15T23:59:59.999",
        )
        results = BaseClient.unwrap(response).get("results", [])
        if not results:
            pytest.skip("No transactions in date range")
        tx = results[0]
        assert "p2p_bankdetails" in tx
        assert "accountNumber" in tx["p2p_bankdetails"]
        assert "phoneNumber" in tx["p2p_bankdetails"]

    def test_response_contains_payment_method(self):
        response = self.client.get_transactions(
            created_range="2026-06-08T00:00:00.000,2026-06-15T23:59:59.999",
        )
        results = BaseClient.unwrap(response).get("results", [])
        if not results:
            pytest.skip("No transactions in date range")
        assert "payment_method" in results[0]


@pytest.mark.api
@pytest.mark.smoke
class TestTransactionFilters:
    @pytest.fixture(autouse=True)
    def setup(self, auth_client):
        self.client = make_client(auth_client)

    def test_filter_partners_returns_list(self):
        response = self.client.get_filter_partners()
        assert response.status_code == 200
        data = BaseClient.unwrap(response)
        assert isinstance(data, list)

    def test_filter_services_returns_list(self):
        response = self.client.get_filter_services()
        assert response.status_code == 200
        data = BaseClient.unwrap(response)
        assert isinstance(data, list)

    def test_filter_statuses_returns_list(self):
        response = self.client.get_filter_statuses()
        assert response.status_code == 200
        data = BaseClient.unwrap(response)
        assert isinstance(data, list)
