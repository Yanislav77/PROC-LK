from playwright.sync_api import Page
from pages.base_page import BasePage


class TerminalEditPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Breadcrumbs (per spec: "Настройки терминалов / Редактирование терминала")
        self.breadcrumb_list = page.get_by_text("Настройки терминалов", exact=True)
        self.breadcrumb_current = page.get_by_text("Редактирование терминала", exact=True)
        # Navigation
        self.back_btn = page.get_by_role("button", name="Назад").or_(
            page.get_by_role("link", name="Назад")
        )
        # Secret key card (per spec: masked, read-only, copy button)
        self.secret_key_input = page.locator("input[name=secret_key]")
        self.copy_btn = page.get_by_role("button", name="Копировать").or_(
            page.locator("[aria-label*='опир']")
        )
        # General settings (per spec)
        # name — недоступно для редактирования (disabled input с badge статуса)
        self.name_input = page.locator("input[name=name]")
        # public_name — доступно для редактирования
        self.public_name_input = page.locator("input[name=public_name]")
        # processing_host — недоступно для редактирования
        self.processing_host_input = page.locator("input[name=processing_host]")
        # is_test — недоступно для редактирования (Режим: Test/Production)
        self.mode_input = page.locator("input[name=is_test]").or_(
            page.locator("[class*='MuiSelect-select']").first
        )
        # Notifications (per spec)
        # is_notify — checkbox (MUI Checkbox не ставит name, ищем по type=checkbox)
        self.is_notify_toggle = page.locator("input[type=checkbox]")
        self.url_success_input = page.locator("input[name=url_success]")
        self.url_error_input = page.locator("input[name=url_error]")
        self.url_notify_input = page.locator("input[name=url_notify]")
        self.return_url_input = page.locator("input[name=return_url]")
        # Form actions
        self.save_btn = page.get_by_role("button", name="Сохранить")
