from playwright.sync_api import Page
from pages.base_page import BasePage


class TransactionsPage(BasePage):
    URL = "/transactions"

    def __init__(self, page: Page):
        super().__init__(page)
        self.tab_payments = page.get_by_role("button", name="Платежи")
        self.tab_payouts = page.get_by_role("button", name="Выплаты")
        self.tab_chargeback = page.get_by_role("button", name="Chargeback")
        self.tab_all = page.get_by_role("button", name="Все").first
        self.apply_btn = page.get_by_role("button", name="Применить")
        self.clear_btn = page.get_by_role("button", name="Очистить")
        self.export_csv = page.get_by_role("button", name="CSV")
        self.export_xlsx = page.get_by_role("button", name="XLSX")
        self.search_input = page.locator("input[name=searchValue]")
        self.rows = page.locator("[role='row']")
        self.transaction_links = page.locator("a[href*='/new/transactions/']")

    def open(self):
        self.navigate(self.URL)

    def get_row_count(self) -> int:
        return self.rows.count()

    def click_transaction(self, index: int = 0):
        self.transaction_links.nth(index).click()

    def switch_tab(self, name: str):
        self.page.get_by_role("button", name=name).click()
        self.page.wait_for_load_state("networkidle")
