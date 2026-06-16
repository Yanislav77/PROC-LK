import threading
import time
from pathlib import Path
import pytest
from utils.config import BASE_URL, HEADLESS, VIDEO, TEST_USER_EMAIL, TEST_USER_PASSWORD
from api_clients.auth_client import AuthClient

VIDEO_DIR = Path("reports/videos")

# (src, dst) — собирается в хуке, переименование выполняется в sessionfinish
_pending_renames: list[tuple[Path, Path]] = []


def _do_login_and_save(state_file: Path):
    """Запускается в отдельном потоке — вне asyncio-цикла pytest-playwright."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(f"{BASE_URL}/login")
        page.locator("input[name=username]").fill(TEST_USER_EMAIL)
        page.locator("input[name=password]").fill(TEST_USER_PASSWORD)
        page.locator("button[type=submit]").click()
        page.wait_for_url("**/dashboard**")
        ctx.storage_state(path=str(state_file))
        browser.close()


@pytest.fixture(scope="session")
def _auth_state_path(tmp_path_factory):
    """Логинится один раз, сохраняет cookies/localStorage в файл."""
    state_file = tmp_path_factory.mktemp("auth") / "state.json"
    t = threading.Thread(target=_do_login_and_save, args=(state_file,))
    t.start()
    t.join()
    return str(state_file)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, _auth_state_path):
    args = {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 900},
        "storage_state": _auth_state_path,
    }
    if VIDEO:
        VIDEO_DIR.mkdir(parents=True, exist_ok=True)
        args["record_video_dir"] = str(VIDEO_DIR)
        args["record_video_size"] = {"width": 1440, "height": 900}
    return args


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Сохраняет report на ноде (для фикстур) и собирает видео для переименования."""
    outcome = yield
    report = outcome.get_result()
    # Сохраняем rep_call / rep_setup / rep_teardown на ноде, чтобы фикстуры
    # могли проверить, упал ли тест (используется для скриншотов при падении).
    setattr(item, f"rep_{report.when}", report)
    if report.when != "teardown":
        return
    src_str = getattr(item, "_video_src", None)
    name = getattr(item, "_video_name", None)
    if not src_str or not name:
        return
    src = Path(src_str)
    dst = src.parent / f"{name}.webm"
    _pending_renames.append((src, dst))


def pytest_sessionfinish(session, exitstatus):
    """После всех тестов переименовывает видеофайлы из хэшей в имена тестов."""
    if not VIDEO:
        return
    for src, dst in _pending_renames:
        for _ in range(100):          # ждём до 10 секунд финализации файла
            if src.exists():
                try:
                    src.replace(dst)
                except OSError:
                    time.sleep(0.3)
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
