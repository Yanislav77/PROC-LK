from playwright.sync_api import Page
from pages.base_page import BasePage


class TfaSetupPage(BasePage):
    URL = "/tfa/setup"

    def __init__(self, page: Page):
        super().__init__(page)
        self.title = page.get_by_role("heading", name="Подключение двухфакторной аутентификации")
        self.instruction = page.get_by_text("Отсканируйте QR-код в приложении-аутентификаторе")
        self.qr_image = page.locator("img[src*='qr'], canvas, svg").first
        self.manual_key_label = page.get_by_text("Или введите код вручную")
        self.secret_text = page.locator("text=/(?:[A-Z2-7]{4} *){3,}/")
        self.code_input = page.locator("input[name='key']")
        self.connect_btn = page.get_by_role("button", name="Подключить")
        self.cancel_btn = page.get_by_role("button", name="Отменить")
        self.error_msg = page.get_by_text("Неверный код")

    def get_secret(self) -> str:
        """Возвращает TOTP-секрет со страницы (без пробелов, готов для pyotp)."""
        self.secret_text.wait_for(state="visible")
        return self.secret_text.inner_text().strip().replace(" ", "")

    def submit_code(self, code: str):
        self.code_input.fill(code)
        self.connect_btn.click()
