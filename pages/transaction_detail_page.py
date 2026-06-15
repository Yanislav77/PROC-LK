from playwright.sync_api import Page
from pages.base_page import BasePage


class TransactionDetailPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.back_link = page.locator("a[href='/new/transactions']")

    def is_loaded(self) -> bool:
        return "/new/transactions/" in self.page.url

    def go_back(self):
        self.back_link.click()
        self.page.wait_for_load_state("networkidle")
