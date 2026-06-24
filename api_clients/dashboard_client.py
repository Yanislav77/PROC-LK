from api_clients.base_client import BaseClient
from utils.config import API_V1_URL, API_V4_URL


class DashboardClient(BaseClient):
    def __init__(self, token: str = None):
        super().__init__(token=token, base_url=API_V4_URL)
        self._v1_url = API_V1_URL

    def get_filter_currencies(self):
        """GET /api/v1/services/filters/currencies/"""
        return self.session.get(f"{self._v1_url}/services/filters/currencies/")

    def post_filter_services(self, partners: list):
        """POST /api/v1/transactions/filters/services/"""
        return self.session.post(
            f"{self._v1_url}/transactions/filters/services/",
            json={"partners": partners},
        )

    def get_statistics(self, **params):
        """GET /api/v1/dashboard/charts/statistics/"""
        return self.session.get(
            f"{self._v1_url}/dashboard/charts/statistics/",
            params=params,
        )

    def get_countries(self, **params):
        """GET /api/v4/dashboard/charts/countries/"""
        return self.get("/dashboard/charts/countries/", params=params)

    def get_payment_systems(self, **params):
        """GET /api/v4/dashboard/charts/ps/"""
        return self.get("/dashboard/charts/ps/", params=params)
