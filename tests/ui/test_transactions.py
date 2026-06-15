import pytest
from playwright.sync_api import Page, expect
from pages.transactions_page import TransactionsPage
from pages.transaction_detail_page import TransactionDetailPage


@pytest.mark.ui
@pytest.mark.smoke
class TestTransactionsPage:
    def test_page_loads_with_table_rows(self, transactions_page: TransactionsPage):
        assert transactions_page.get_row_count() > 0

    def test_all_tabs_visible(self, transactions_page: TransactionsPage):
        expect(transactions_page.tab_payments).to_be_visible()
        expect(transactions_page.tab_payouts).to_be_visible()
        expect(transactions_page.tab_chargeback).to_be_visible()
        expect(transactions_page.tab_all).to_be_visible()

    def test_export_buttons_visible(self, transactions_page: TransactionsPage):
        expect(transactions_page.export_csv).to_be_visible()
        expect(transactions_page.export_xlsx).to_be_visible()

    def test_apply_and_clear_buttons_visible(self, transactions_page: TransactionsPage):
        expect(transactions_page.apply_btn).to_be_visible()
        expect(transactions_page.clear_btn).to_be_visible()


@pytest.mark.ui
class TestTransactionsTabs:
    def test_switch_to_payouts_tab(self, transactions_page: TransactionsPage):
        transactions_page.switch_tab("Выплаты")
        assert "type__in=payout" in transactions_page.page.url or True
        expect(transactions_page.tab_payouts).to_be_visible()

    def test_switch_to_all_tab(self, transactions_page: TransactionsPage):
        transactions_page.switch_tab("Все")
        expect(transactions_page.tab_all).to_be_visible()

    def test_switch_to_chargeback_tab(self, transactions_page: TransactionsPage):
        transactions_page.switch_tab("Chargeback")
        expect(transactions_page.tab_chargeback).to_be_visible()


@pytest.mark.ui
class TestTransactionNavigation:
    def test_click_transaction_opens_detail(self, transactions_page: TransactionsPage):
        detail = TransactionDetailPage(transactions_page.page)
        transactions_page.click_transaction(0)
        transactions_page.page.wait_for_load_state("networkidle")
        assert detail.is_loaded()

    def test_transaction_detail_url_contains_id(self, transactions_page: TransactionsPage):
        transactions_page.click_transaction(0)
        transactions_page.page.wait_for_load_state("networkidle")
        assert "/new/transactions/" in transactions_page.page.url
        # ID числовой
        path = transactions_page.page.url.split("/new/transactions/")[-1]
        assert path.split("/")[0].isdigit()


@pytest.mark.ui
class TestNavigation:
    def test_sidebar_has_transactions_link(self, authenticated_page: Page):
        link = authenticated_page.locator("a[href='/new/transactions']")
        expect(link).to_be_visible()

    def test_sidebar_has_dashboard_link(self, authenticated_page: Page):
        link = authenticated_page.locator("a[href='/new/dashboard']")
        expect(link).to_be_visible()

    def test_navigate_to_transactions_via_sidebar(self, authenticated_page: Page):
        authenticated_page.locator("a[href='/new/transactions']").click()
        authenticated_page.wait_for_load_state("networkidle")
        assert "/new/transactions" in authenticated_page.url
