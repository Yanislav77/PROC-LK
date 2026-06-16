import base64
import re
from pathlib import Path

import pytest
import pytest_html
from playwright.sync_api import Page

from pages.login_page import LoginPage
from utils.config import BASE_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD, VIDEO

SCREENSHOTS_DIR = Path("reports/screenshots")


def _safe_name(nodeid: str) -> str:
    parts = nodeid.split("::")
    name_parts = [p for p in parts[1:] if p]
    name = "__".join(name_parts[-2:] if len(name_parts) >= 2 else name_parts[-1:])
    name = re.sub(r"\[.*?\]", "", name)
    return re.sub(r"[^\w]", "_", name)[:120]


def _ensure_authenticated(page: Page) -> None:
    """Если сессия инвалидирована (редирект на /login) — логинимся заново."""
    if "/login" in page.url:
        page.locator("input[name=username]").fill(TEST_USER_EMAIL)
        page.locator("input[name=password]").fill(TEST_USER_PASSWORD)
        page.locator("button[type=submit]").click()
        page.wait_for_url("**/dashboard**")
        page.wait_for_load_state("networkidle")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Описание теста и скриншот при падении — прикрепляет к HTML-отчёту."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    report.extras = getattr(report, "extras", [])

    description = (item.function.__doc__ or "").strip()
    if description:
        report.extras.insert(0, pytest_html.extras.text(description, name="Описание"))

    if not report.failed:
        return
    page: Page = item.funcargs.get("page")
    if page is None:
        return
    try:
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        path = SCREENSHOTS_DIR / f"{_safe_name(item.nodeid)}.png"
        raw = page.screenshot(path=str(path), full_page=True)
        b64 = base64.b64encode(raw).decode("utf-8")
        report.extras.append(
            pytest_html.extras.image(f"data:image/png;base64,{b64}", name="screenshot")
        )
    except Exception:
        pass


@pytest.fixture(autouse=True)
def _store_video_path(page: Page, request):
    """Сохраняет путь к видео до закрытия страницы, чтобы хук мог переименовать файл."""
    yield
    if not VIDEO or not page.video:
        return
    try:
        request.node._video_src = str(page.video.path())
        request.node._video_name = _safe_name(request.node.nodeid)
    except Exception:
        pass


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    lp = LoginPage(page)
    lp.open()
    return lp


@pytest.fixture
def authenticated_page(page: Page) -> Page:
    page.goto(f"{BASE_URL}/dashboard")
    page.wait_for_load_state("networkidle")
    _ensure_authenticated(page)
    return page


