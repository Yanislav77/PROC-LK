import pytest
from pages.login_page import LoginPage
from utils.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


@pytest.mark.ui
@pytest.mark.smoke
class TestLogin:
    def test_successful_login(self, login_page: LoginPage):
        login_page.open()
        login_page.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        login_page.page.wait_for_url("**/dashboard**")

    def test_invalid_credentials(self, login_page: LoginPage):
        login_page.open()
        login_page.login("wrong@example.com", "wrongpassword")
        assert login_page.error_msg.is_visible()

    def test_empty_fields(self, login_page: LoginPage):
        login_page.open()
        login_page.submit_btn.click()
        assert login_page.error_msg.is_visible()
