import pytest
from api_clients.auth_client import AuthClient
from utils.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


@pytest.fixture(scope="module")
def auth_client() -> AuthClient:
    client = AuthClient()
    response = client.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    assert response.status_code == 200, (
        f"Авторизация не удалась: HTTP {response.status_code}. "
        f"Проверьте TEST_USER_EMAIL / TEST_USER_PASSWORD в .env. "
        f"Ответ сервера: {response.text[:300]}"
    )
    token = response.json()["response"]["access"]
    return AuthClient(token=token)
