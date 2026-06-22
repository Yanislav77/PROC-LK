from playwright.sync_api import Page
from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "/login"

    def __init__(self, page: Page):
        super().__init__(page)
        self.title = page.get_by_role("heading", name="Вход в личный кабинет")
        self.username_input = page.locator("input[name=username]")
        self.password_input = page.locator("input[name=password]")
        self.submit_btn = page.locator("button[type=submit]")
        self.error_msg = page.locator("[class*='error']:visible").last
        # Eye icon button inside password field (MUI InputAdornment)
        self.toggle_password_btn = page.locator("[class*='MuiIconButton-root']")
        self.forgot_password_link = page.get_by_role("link", name="Забыли пароль?")

    def open(self):
        self.navigate(self.URL)

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_btn.click()
