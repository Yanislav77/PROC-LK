import pytest
from utils.config import HEADLESS, VIDEO, TEST_USER_EMAIL, TEST_USER_PASSWORD
from api_clients.auth_client import AuthClient

VIDEO_DIR = "reports/videos"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    args = {**browser_context_args, "viewport": {"width": 1440, "height": 900}}
    if VIDEO:
        args["record_video_dir"] = VIDEO_DIR
        args["record_video_size"] = {"width": 1440, "height": 900}
    return args


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
