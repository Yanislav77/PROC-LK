from api_clients.base_client import BaseClient
from utils.config import API_V1_URL


class ServicesClient(BaseClient):
    def __init__(self, token: str = None):
        super().__init__(token=token, base_url=API_V1_URL)

    def get_terminal(self, service_id: int):
        return self.get(f"/services/{service_id}/")

    def update_terminal(self, service_id: int, payload: dict):
        return self.put(f"/services/{service_id}/", json=payload)

    def get_terminals_list(self, **params):
        return self.get("/services/", params=params)
