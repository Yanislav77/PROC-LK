from playwright.sync_api import Page
from pages.base_page import BasePage


class TerminalEditPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Breadcrumbs
        self.breadcrumb_list = page.get_by_text("Настройки терминалов")
        self.breadcrumb_current = page.get_by_text("Редактирование терминала")
        # Navigation
        self.back_btn = page.get_by_role("button", name="Назад").or_(
            page.get_by_role("link", name="Назад")
        )
        # Secret key card
        self.secret_key_input = page.locator("input[name=secret_key]")
        self.copy_btn = page.get_by_role("button", name="Копировать").or_(
            page.locator("[aria-label*='опир']")
        )
        # General settings
        self.name_input = page.locator("input[name=name]")
        self.public_name_input = page.locator("input[name=public_name]")
        self.processing_host_input = page.locator("input[name=processing_host]")
        # is_test displayed as "Test" / "Production" (read-only)
        self.mode_input = page.locator("input[name=is_test]").or_(
            page.locator("[data-field=is_test]")
        )
        # Notifications
        self.is_notify_toggle = (
            page.locator("input[name=is_notify]")
            .or_(page.locator("[role=checkbox][name=is_notify]"))
            .or_(page.locator("[role=switch]"))
        )
        self.url_success_input = page.locator("input[name=url_success]")
        self.url_error_input = page.locator("input[name=url_error]")
        self.url_notify_input = page.locator("input[name=url_notify]")
        self.return_url_input = page.locator("input[name=return_url]")
        # Form actions
        self.save_btn = page.get_by_role("button", name="Сохранить")
