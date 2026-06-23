from playwright.sync_api import Page
from pages.base_page import BasePage


class TfaLoginPage(BasePage):
    URL = "/tfa/verify"

    def __init__(self, page: Page):
        super().__init__(page)
        self.title = page.get_by_role("heading", name="Двухфакторная аутентификация")
        self.subtitle = page.get_by_text("Введите код из приложения-аутентификатора")
        self.code_input = page.locator("input[name='key']")
        self.submit_btn = page.get_by_role("button", name="Подтвердить")
        self.logout_btn = page.get_by_role("button", name="Выйти")
        self.error_msg = page.get_by_text("Неверный код")

    def submit_code(self, code: str):
        self.code_input.fill(code)
        self.submit_btn.click()
