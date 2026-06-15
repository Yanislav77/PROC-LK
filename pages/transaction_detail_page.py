from playwright.sync_api import Page
from pages.base_page import BasePage


class TransactionDetailPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Three <a href='/new/transactions'> exist (sidebar, breadcrumb, back button)
        # Target only the back button (MuiButton-root)
        self.back_link = page.locator("a[href='/new/transactions'][class*='MuiButton-root']")
        self.title = page.locator("h1")
        self.refund_btn = page.get_by_role("button", name="Возврат")
        self.send_webhook_btn = page.get_by_role("button", name="Отправить вебхук")
        self.section_history = page.locator("h2").filter(has_text="История статусов")
        self.section_payment_details = page.locator("h2").filter(has_text="Детали платежа")
        self.section_payment_data = page.locator("h2").filter(has_text="Платежные данные")

    def is_loaded(self) -> bool:
        return "/new/transactions/" in self.page.url

    def go_back(self):
        self.back_link.click()
        self.page.wait_for_load_state("networkidle")
