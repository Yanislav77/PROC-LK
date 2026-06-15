from playwright.sync_api import Page
from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "/login"

    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input = page.locator('[data-testid="email"]')
        self.password_input = page.locator('[data-testid="password"]')
        self.submit_btn = page.locator('[data-testid="submit"]')
        self.error_msg = page.locator('[data-testid="error-message"]')

    def open(self):
        self.navigate(self.URL)

    def login(self, email: str, password: str):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_btn.click()
