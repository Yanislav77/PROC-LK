import re
import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.transactions_page import TransactionsPage
from utils.config import TEST_USER_EMAIL, TEST_USER_PASSWORD, VIDEO


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
    lp = LoginPage(page)
    lp.open()
    lp.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    page.wait_for_url("**/dashboard**")
    page.wait_for_load_state("networkidle")
    return page


@pytest.fixture
def transactions_page(authenticated_page: Page) -> TransactionsPage:
    tp = TransactionsPage(authenticated_page)
    tp.open()
    authenticated_page.wait_for_load_state("networkidle")
    return tp
