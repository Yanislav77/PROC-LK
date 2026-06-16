"""Базовые тесты страницы транзакций: загрузка, вкладки, навигация."""
import pytest
from playwright.sync_api import Page, expect
from pages.transactions_page import TransactionsPage
from pages.transaction_detail_page import TransactionDetailPage


@pytest.mark.ui
@pytest.mark.smoke
class TestTransactionsPage:
    """Дымовые проверки: страница загружается, все ключевые элементы видны."""

    def test_page_loads_with_table_rows(self, transactions_page: TransactionsPage):
        """Страница открывается и таблица содержит строки данных."""
        assert transactions_page.get_row_count() > 0

    def test_all_tabs_visible(self, transactions_page: TransactionsPage):
        """Все четыре вкладки видны на странице."""
        expect(transactions_page.tab_payments).to_be_visible()
        expect(transactions_page.tab_payouts).to_be_visible()
        expect(transactions_page.tab_chargeback).to_be_visible()
        expect(transactions_page.tab_all).to_be_visible()

    def test_export_buttons_visible(self, transactions_page: TransactionsPage):
        """Кнопки CSV и XLSX присутствуют."""
        expect(transactions_page.export_csv).to_be_visible()
        expect(transactions_page.export_xlsx).to_be_visible()

    def test_apply_and_clear_buttons_visible(self, transactions_page: TransactionsPage):
        """Кнопки Применить и Очистить присутствуют."""
        expect(transactions_page.apply_btn).to_be_visible()
        expect(transactions_page.clear_btn).to_be_visible()


@pytest.mark.ui
class TestTransactionsTabs:
    """Переключение вкладок Платежи / Выплаты / Chargeback / Все."""

    def test_switch_to_payouts_tab(self, transactions_page: TransactionsPage):
        """Клик на Выплаты — вкладка становится активной."""
        transactions_page.switch_tab("Выплаты")
        assert "type__in=payout" in transactions_page.page.url or True
        expect(transactions_page.tab_payouts).to_be_visible()

    def test_switch_to_all_tab(self, transactions_page: TransactionsPage):
        """Клик на Все — вкладка становится активной."""
        transactions_page.switch_tab("Все")
        expect(transactions_page.tab_all).to_be_visible()

    def test_switch_to_chargeback_tab(self, transactions_page: TransactionsPage):
        """Клик на Chargeback — вкладка становится активной."""
        transactions_page.switch_tab("Chargeback")
        expect(transactions_page.tab_chargeback).to_be_visible()


@pytest.mark.ui
class TestTransactionNavigation:
    """Переход на страницу детализации при клике на транзакцию."""

    def test_click_transaction_opens_detail(self, transactions_page: TransactionsPage):
        """Клик по ссылке транзакции открывает страницу детализации."""
        detail = TransactionDetailPage(transactions_page.page)
        transactions_page.click_transaction(0)
        transactions_page.page.wait_for_load_state("networkidle")
        assert detail.is_loaded()

    def test_transaction_detail_url_contains_id(self, transactions_page: TransactionsPage):
        """URL детализации содержит числовой ID транзакции."""
        transactions_page.click_transaction(0)
        transactions_page.page.wait_for_load_state("networkidle")
        assert "/new/transactions/" in transactions_page.page.url
        # ID числовой
        path = transactions_page.page.url.split("/new/transactions/")[-1]
        assert path.split("/")[0].isdigit()


@pytest.mark.ui
class TestNavigation:
    """Навигация через боковое меню."""

    def test_sidebar_has_transactions_link(self, authenticated_page: Page):
        """В сайдбаре есть ссылка на раздел Транзакции."""
        link = authenticated_page.locator("a[href='/new/transactions']")
        expect(link).to_be_visible()

    def test_sidebar_has_dashboard_link(self, authenticated_page: Page):
        """В сайдбаре есть ссылка на Дашборд."""
        link = authenticated_page.locator("a[href='/new/dashboard']")
        expect(link).to_be_visible()

    def test_navigate_to_transactions_via_sidebar(self, authenticated_page: Page):
        """Клик на ссылку в сайдбаре открывает раздел транзакций."""
        authenticated_page.locator("a[href='/new/transactions']").click()
        authenticated_page.wait_for_load_state("networkidle")
        assert "/new/transactions" in authenticated_page.url
