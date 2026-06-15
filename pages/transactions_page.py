from playwright.sync_api import Page
from pages.base_page import BasePage


class TransactionsPage(BasePage):
    URL = "/transactions"

    def __init__(self, page: Page):
        super().__init__(page)
        # Tabs
        self.tab_payments = page.get_by_role("button", name="Платежи")
        self.tab_payouts = page.get_by_role("button", name="Выплаты")
        self.tab_chargeback = page.get_by_role("button", name="Chargeback")
        self.tab_all = page.get_by_role("button", name="Все").first
        # Filter buttons
        self.apply_btn = page.get_by_role("button", name="Применить")
        self.clear_btn = page.get_by_role("button", name="Очистить")
        # Filter labels (MUI labels have no `for` attribute — locate by text)
        self.filter_label_date_type = page.locator("label").filter(has_text="Дата (тип)")
        self.filter_label_terminal = page.locator("label").filter(has_text="Терминал")
        self.filter_label_organization = page.locator("label").filter(has_text="Организация")
        self.filter_label_status = page.locator("label").filter(has_text="Статус")
        self.filter_label_method = page.locator("label").filter(has_text="Метод")
        self.filter_label_mode = page.locator("label").filter(has_text="Режим")
        # Filter comboboxes (positional, order matches label order on page)
        _comboboxes = page.locator("[role='combobox']")
        self.filter_date_type_select = _comboboxes.nth(0)   # Дата (тип)
        self.filter_terminal_select = _comboboxes.nth(1)    # Терминал
        self.filter_organization_select = _comboboxes.nth(2)  # Организация
        self.filter_status_select = _comboboxes.nth(3)      # Статус
        self.filter_method_select = _comboboxes.nth(4)      # Метод
        self.filter_mode_select = _comboboxes.nth(5)        # Режим
        self.search_type_select = _comboboxes.nth(6)        # Параметр поиска
        self.page_size_select = _comboboxes.nth(7)          # 10 (размер страницы)
        # Search input
        self.search_input = page.locator("input[name=searchValue]")
        # Export buttons
        self.export_csv = page.get_by_role("button", name="CSV")
        self.export_xlsx = page.get_by_role("button", name="XLSX")
        # Table
        self.rows = page.locator("[role='row']")
        self.transaction_links = page.locator("a[href*='/new/transactions/']")
        # Action buttons
        self.refund_btn = page.get_by_role("button", name="Возврат")
        self.send_webhook_btn = page.get_by_role("button", name="Отправить вебхук")
        self.request_status_btn = page.get_by_role("button", name="Запросить статус")

    def open(self):
        self.navigate(self.URL)

    def get_row_count(self) -> int:
        return self.rows.count()

    def click_transaction(self, index: int = 0):
        self.transaction_links.nth(index).click()

    def click_data_row(self, index: int = 0):
        """Click a data row to select it (skips header row at index 0)."""
        self.rows.nth(index + 1).click()
        self.page.wait_for_timeout(300)

    def switch_tab(self, name: str):
        self.page.get_by_role("button", name=name).click()
        self.page.wait_for_load_state("networkidle")

    def get_pagination_button(self, page_num: int):
        return self.page.get_by_role("button", name=str(page_num), exact=True)
