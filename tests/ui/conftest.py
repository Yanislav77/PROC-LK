import re
import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.transactions_page import TransactionsPage
from utils.config import BASE_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD, VIDEO


def _ensure_authenticated(page: Page) -> None:
    """Если сессия инвалидирована (редирект на /login) — логинимся заново."""
    if "/login" in page.url:
        page.locator("input[name=username]").fill(TEST_USER_EMAIL)
        page.locator("input[name=password]").fill(TEST_USER_PASSWORD)
        page.locator("button[type=submit]").click()
        page.wait_for_url("**/dashboard**")
        page.wait_for_load_state("networkidle")


@pytest.fixture(autouse=True)
def _store_video_path(page: Page, request):
    """Сохраняет путь к видео до закрытия страницы, чтобы хук мог переименовать файл."""
    yield
    if not VIDEO or not page.video:
        return
    try:
        request.node._video_src = str(page.video.path())
        parts = request.node.nodeid.split("::")
        name_parts = [p for p in parts[1:] if p]  # убираем путь к файлу
        name = "__".join(name_parts[-2:] if len(name_parts) >= 2 else name_parts[-1:])
        name = re.sub(r"\[.*?\]", "", name)         # убираем [chromium]
        name = re.sub(r"[^\w]", "_", name)[:120]    # sanitize
        request.node._video_name = name
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


@pytest.fixture
def transactions_page(page: Page) -> TransactionsPage:
    tp = TransactionsPage(page)
    tp.open()
    page.wait_for_load_state("networkidle")
    _ensure_authenticated(page)
    # После повторного логина оказываемся на dashboard — возвращаемся к транзакциям
    if "/transactions" not in page.url:
        tp.open()
        page.wait_for_load_state("networkidle")
    tp.rows.first.wait_for(state="visible", timeout=30000)
    return tp
