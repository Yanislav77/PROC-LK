from api_clients.base_client import BaseClient


class AuthClient(BaseClient):
    def login(self, username: str, password: str):
        return self.post("/auth/token/", json={"username": username, "password": password})

    def refresh(self, refresh_token: str):
        return self.post("/auth/token/refresh/", json={"refresh": refresh_token})
