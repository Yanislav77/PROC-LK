from playwright.sync_api import Page


class Sidebar:
    def __init__(self, page: Page):
        self.page = page
        self.dashboard_link = page.locator("a[href='/new/dashboard']")
        self.transactions_link = page.locator("a[href='/new/transactions']")
        self.terminals_link = page.locator("a[href='/new/terminals']")
        self.logout_btn = page.locator("button:has-text('Выход'), a:has-text('Выход')")

    def go_to_dashboard(self):
        self.dashboard_link.click()
        self.page.wait_for_load_state("networkidle")

    def go_to_transactions(self):
        self.transactions_link.click()
        self.page.wait_for_load_state("networkidle")

    def go_to_terminals(self):
        self.terminals_link.click()
        self.page.wait_for_load_state("networkidle")

    def is_visible(self) -> bool:
        return self.dashboard_link.is_visible()
