import requests
from utils.config import API_V4_URL


class BaseClient:
    def __init__(self, token: str = None, base_url: str = None):
        self.base_url = base_url or API_V4_URL
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        self.session.headers["Content-Type"] = "application/json"

    def get(self, path: str, **kwargs):
        return self.session.get(f"{self.base_url}{path}", **kwargs)

    def post(self, path: str, **kwargs):
        return self.session.post(f"{self.base_url}{path}", **kwargs)

    def put(self, path: str, **kwargs):
        return self.session.put(f"{self.base_url}{path}", **kwargs)

    def delete(self, path: str, **kwargs):
        return self.session.delete(f"{self.base_url}{path}", **kwargs)

    @staticmethod
    def unwrap(response):
        """Извлекает data['response'] из стандартного ответа API."""
        return response.json()["response"]
