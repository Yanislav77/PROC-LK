import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from utils.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def authenticated_page(page: Page) -> Page:
    lp = LoginPage(page)
    lp.open()
    lp.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    page.wait_for_url("**/dashboard**")
    return page
