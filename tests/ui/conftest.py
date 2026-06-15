import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.transactions_page import TransactionsPage
from utils.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


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
