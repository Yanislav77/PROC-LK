import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from utils.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


@pytest.fixture
def browser_context_args(browser_context_args):
    # Логин-тесты проверяют форму — убираем storage_state, чтобы стартовать незалогиненным
    return {k: v for k, v in browser_context_args.items() if k != "storage_state"}


@pytest.mark.ui
@pytest.mark.smoke
class TestLogin:
    def test_successful_login_redirects_to_dashboard(self, login_page: LoginPage):
        login_page.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        login_page.page.wait_for_url("**/dashboard**")
        assert "/new/dashboard" in login_page.page.url

    def test_invalid_credentials_shows_error(self, login_page: LoginPage):
        login_page.login("wrong@example.com", "wrongpassword")
        login_page.page.wait_for_timeout(1500)
        assert login_page.error_msg.is_visible()
        assert login_page.error_msg.inner_text().strip() != ""

    def test_wrong_password_stays_on_login(self, login_page: LoginPage):
        login_page.login(TEST_USER_EMAIL, "wrongpassword")
        login_page.page.wait_for_timeout(1500)
        assert "/new/login" in login_page.page.url

    def test_login_page_has_forgot_password_link(self, login_page: LoginPage):
        forgot = login_page.page.locator("a[href='/new/forgot-password']")
        expect(forgot).to_have_count(1)
