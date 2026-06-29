import requests
from utils.config import API_V4_URL


class AuthV4Client:
    """Клиент для v4 эндпоинтов авторизации (refreshToken через HttpOnly cookie)."""

    def __init__(self):
        self.base_url = API_V4_URL
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"

    def login(self, username: str, password: str):
        return self.session.post(
            f"{self.base_url}/auth/token/",
            json={"username": username, "password": password},
        )

    def refresh(self):
        """Refresh, используя refreshToken cookie из текущей сессии."""
        return self.session.post(f"{self.base_url}/auth/token/refresh/", json={})

    def refresh_with_cookie(self, token_value: str):
        """Refresh с явно переданным значением refreshToken (новая сессия, без session cookie)."""
        return requests.post(
            f"{self.base_url}/auth/token/refresh/",
            json={},
            headers={"Content-Type": "application/json"},
            cookies={"refreshToken": token_value},
        )

    def logout(self):
        return self.session.post(f"{self.base_url}/auth/logout/", json={})
