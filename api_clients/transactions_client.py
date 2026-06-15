from api_clients.base_client import BaseClient
from utils.config import API_V1_URL, API_V4_URL


class TransactionsClient(BaseClient):
    def __init__(self, token: str = None):
        super().__init__(token=token, base_url=API_V4_URL)
        self._v1_url = API_V1_URL

    def get_transactions(
        self,
        created_range: str = None,
        type_in: str = None,
        page: int = 1,
        size: int = 10,
    ):
        params = {"page": page, "size": size}
        if created_range:
            params["created__range"] = created_range
        if type_in:
            params["type__in"] = type_in
        return self.get("/transactions/", params=params)

    def get_filter_partners(self):
        return self.session.get(f"{self._v1_url}/transactions/filters/partners/")

    def get_filter_services(self):
        return self.session.get(f"{self._v1_url}/transactions/filters/services/")

    def get_filter_statuses(self):
        return self.session.get(f"{self._v1_url}/transactions/filters/statuses/")
