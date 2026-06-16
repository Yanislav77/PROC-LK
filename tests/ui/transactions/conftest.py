import pytest
from playwright.sync_api import Page

from pages.transactions_page import TransactionsPage
from utils.config import BASE_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD


def _ensure_authenticated(page: Page) -> None:
    """Если сессия инвалидирована (редирект на /login) — логинимся заново."""
    if "/login" in page.url:
        page.locator("input[name=username]").fill(TEST_USER_EMAIL)
        page.locator("input[name=password]").fill(TEST_USER_PASSWORD)
        page.locator("button[type=submit]").click()
        page.wait_for_url("**/dashboard**")
        page.wait_for_load_state("networkidle")


@pytest.fixture
def transactions_page(page: Page) -> TransactionsPage:
    tp = TransactionsPage(page)
    tp.open()
    page.wait_for_load_state("networkidle")
    _ensure_authenticated(page)
    if "/transactions" not in page.url:
        tp.open()
        page.wait_for_load_state("networkidle")
    tp.rows.first.wait_for(state="visible", timeout=30000)
    return tp
