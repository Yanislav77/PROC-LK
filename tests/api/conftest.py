import pytest
from api_clients.auth_client import AuthClient
from utils.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


@pytest.fixture(scope="module")
def auth_client() -> AuthClient:
    client = AuthClient()
    response = client.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    token = response.json()["response"]["access"]
    return AuthClient(token=token)
