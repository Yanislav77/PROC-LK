import re
import time
from pathlib import Path
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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Переименовывает видео после полного закрытия контекста (when=teardown)."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "teardown":
        return
    src_str = getattr(item, "_video_src", None)
    name = getattr(item, "_video_name", None)
    if not src_str or not name:
        return
    src = Path(src_str)
    dst = src.parent / f"{name}.webm"
    for _ in range(20):   # ждём до 2 с пока контекст допишет файл
        if src.exists():
            try:
                src.rename(dst)
            except OSError:
                pass
            break
        time.sleep(0.1)


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
