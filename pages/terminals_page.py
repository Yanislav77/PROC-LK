from playwright.sync_api import Page
from pages.base_page import BasePage


class TerminalsPage(BasePage):
    URL = "/terminals"

    def __init__(self, page: Page):
        super().__init__(page)
        self.title = page.get_by_role("heading", name="Настройки терминалов")
        # Filters
        self.filter_name_input = page.locator("input[name=name__icontains]")
        _comboboxes = page.locator("[role=combobox]")
        self.filter_org_select = _comboboxes.nth(0)
        self.filter_currency_select = _comboboxes.nth(1)
        self.filter_mode_select = _comboboxes.nth(2)
        self.filter_status_select = _comboboxes.nth(3)
        self.page_size_select = _comboboxes.nth(4)
        # Buttons
        self.apply_btn = page.get_by_role("button", name="Применить")
        self.clear_btn = page.get_by_role("button", name="Очистить")
        # Table
        self.rows = page.locator("[role=row]")
        self.column_header = page.locator("[role=columnheader]")
        # Pagination
        self.pagination = page.locator("[role=navigation]")
        self.page_btn_1 = page.get_by_role("button", name="1", exact=True)

    def open(self):
        self.navigate(self.URL)

    def get_row_count(self) -> int:
        return self.rows.count()

    def click_first_terminal_link(self):
        # Gear icon (Настройка column) links to /new/terminals/{id}
        self.rows.first.locator("a[href*='/terminals/']").first.click()
