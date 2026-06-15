import pytest
from api_clients.auth_client import AuthClient
from utils.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


@pytest.mark.api
@pytest.mark.smoke
class TestAuth:
    def test_login_success(self):
        client = AuthClient()
        response = client.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "success"
        assert "access" in data["response"]

    def test_login_invalid_password(self):
        client = AuthClient()
        response = client.login(TEST_USER_EMAIL, "wrongpassword")
        assert response.status_code in (400, 401)

    def test_login_missing_username(self):
        client = AuthClient()
        response = client.post("/auth/token/", json={"password": TEST_USER_PASSWORD})
        assert response.status_code == 400
