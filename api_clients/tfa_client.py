from api_clients.base_client import BaseClient


class TfaClient(BaseClient):
    def verify_tfa(self, code: str, access_token: str):
        """POST /api/v4/auth/tfa — верификация TFA при входе."""
        return self.post("/auth/tfa/", json={"key": code},
                         headers={"Authorization": f"Bearer {access_token}"})

    def connect_tfa(self, code: str, access_token: str):
        """PUT /api/v4/account/tfa — подключение TFA для аккаунта."""
        return self.put("/account/tfa/", json={"use_tfa": True, "key": code},
                        headers={"Authorization": f"Bearer {access_token}"})

    def disable_tfa(self, access_token: str):
        """PUT /api/v4/account/tfa — отключение TFA для аккаунта."""
        return self.put("/account/tfa/", json={"use_tfa": False},
                        headers={"Authorization": f"Bearer {access_token}"})
