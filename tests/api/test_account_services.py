import pytest
from api_clients.account_client import AccountClient
from api_clients.transactions_client import TransactionsClient
from api_clients.base_client import BaseClient

DATE_RANGE = "2026-06-08T00:00:00.000,2026-06-15T23:59:59.999"


def make_token(auth_client) -> str:
    return auth_client.session.headers.get("Authorization", "").removeprefix("Bearer ")


@pytest.mark.api
@pytest.mark.smoke
class TestAccountServices:
    @pytest.fixture(autouse=True)
    def setup(self, auth_client):
        token = make_token(auth_client)
        self.client = AccountClient(token=token)
        self.tx_client = TransactionsClient(token=token)

    def _get_first_partner_id(self) -> int:
        response = self.tx_client.get_filter_partners()
        partners = BaseClient.unwrap(response)
        if not partners:
            pytest.skip("No partners available")
        return partners[0]["id"]

    def test_get_services_returns_success(self):
        partner_id = self._get_first_partner_id()
        response = self.client.get_services([partner_id])
        assert response.status_code == 200
        assert response.json()["message"] == "success"

    def test_get_services_response_is_list(self):
        partner_id = self._get_first_partner_id()
        response = self.client.get_services([partner_id])
        data = BaseClient.unwrap(response)
        assert isinstance(data, list)

    def test_get_services_response_structure(self):
        partner_id = self._get_first_partner_id()
        response = self.client.get_services([partner_id])
        data = BaseClient.unwrap(response)
        assert len(data) > 0
        item = data[0]
        assert "partner_id" in item
        assert "partner_name" in item
        assert "services" in item
        assert isinstance(item["services"], list)

    def test_get_services_each_service_has_id_and_name(self):
        partner_id = self._get_first_partner_id()
        response = self.client.get_services([partner_id])
        data = BaseClient.unwrap(response)
        for partner in data:
            for service in partner["services"]:
                assert "id" in service
                assert "name" in service

    def test_get_services_multiple_partners(self):
        response = self.tx_client.get_filter_partners()
        partners = BaseClient.unwrap(response)
        if len(partners) < 2:
            pytest.skip("Need at least 2 partners")
        ids = [p["id"] for p in partners[:2]]
        response = self.client.get_services(ids)
        assert response.status_code == 200

    def test_get_services_empty_partners_no_500(self):
        response = self.client.get_services([])
        assert response.status_code != 500

    def test_get_services_invalid_partner_no_500(self):
        response = self.client.get_services([999999999])
        assert response.status_code != 500
