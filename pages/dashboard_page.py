from playwright.sync_api import Page
from pages.base_page import BasePage


class DashboardPage(BasePage):
    URL = "/dashboard"

    def __init__(self, page: Page):
        super().__init__(page)

        _comboboxes = page.locator("[role=combobox]")
        self.filter_terminal = _comboboxes.nth(0)
        self.filter_currency = _comboboxes.nth(1)
        self.filter_type = _comboboxes.nth(2)
        self.filter_period = _comboboxes.nth(3)

        # Datepicker groups (always visible)
        self.datepicker_from = page.locator("[role=group]").filter(has_text="Дата с")
        self.datepicker_to = page.locator("[role=group]").filter(has_text="Дата по")

        # Show button
        self.show_btn = page.get_by_role("button", name="Показать")

        # KPI card labels
        self.kpi_turnover_label = page.get_by_text("Сумма оборота", exact=False)
        self.kpi_transactions_label = page.get_by_text("Количество транзакций", exact=False)
        self.kpi_conversion_label = page.get_by_text("Конверсия", exact=False).first

        # Widget labels
        self.widget_countries = page.get_by_text("Страны", exact=False).first
        self.widget_ps = page.get_by_text("Платёжные системы", exact=False).first

        # Widget toggles — buttons by text
        _all_buttons = page.locator("button")
        self.countries_toggle_amount = _all_buttons.filter(has_text="Сумма").nth(0)
        self.countries_toggle_count = _all_buttons.filter(has_text="олличество").nth(0)
        self.countries_toggle_conversion = _all_buttons.filter(has_text="Конверсия").nth(0)
        self.ps_toggle_amount = _all_buttons.filter(has_text="Сумма").nth(1)
        self.ps_toggle_count = _all_buttons.filter(has_text="олличество").nth(1)
        self.ps_toggle_conversion = _all_buttons.filter(has_text="Конверсия").nth(1)

    def open(self):
        self.navigate(self.URL)
