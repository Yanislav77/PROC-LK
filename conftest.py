import pytest
from utils.config import HEADLESS, TEST_USER_EMAIL, TEST_USER_PASSWORD
from api_clients.auth_client import AuthClient


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1440, "height": 900}}


@pytest.fixture(scope="session")
def launch_browser_args():
    return {"headless": HEADLESS}


@pytest.fixture(scope="session")
def auth_token():
    client = AuthClient()
    response = client.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    response.raise_for_status()
    return response.json()["response"]["access"]


@pytest.fixture
def api_client(auth_token):
    return AuthClient(token=auth_token)
