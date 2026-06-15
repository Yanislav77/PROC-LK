from api_clients.base_client import BaseClient


class AccountClient(BaseClient):
    def get_services(self, partner_ids: list):
        return self.post("/account/services/", json={"partners": partner_ids})
