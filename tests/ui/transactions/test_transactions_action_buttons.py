"""Проверяем кнопки действий: Запросить статус, Отправить вебхук, Возврат."""
import pytest
from playwright.sync_api import expect

from pages.transactions_page import TransactionsPage


@pytest.mark.ui
class TestActionButtonsVisibility:
    """Все три кнопки действий отображаются на странице."""

    def test_request_status_button_visible(self, transactions_page: TransactionsPage):
        """Кнопка 'Запросить статус' отображается на странице."""
        expect(transactions_page.request_status_btn).to_be_visible()

    def test_send_webhook_button_visible(self, transactions_page: TransactionsPage):
        """Кнопка 'Отправить вебхук' отображается на странице."""
        expect(transactions_page.send_webhook_btn).to_be_visible()

    def test_refund_button_visible(self, transactions_page: TransactionsPage):
        """Кнопка 'Возврат' отображается на странице."""
        expect(transactions_page.refund_btn).to_be_visible()


@pytest.mark.ui
class TestActionButtonsDefaultState:
    """Без выбора транзакции все кнопки действий недоступны (disabled)."""

    def test_request_status_disabled_without_selection(self, transactions_page: TransactionsPage):
        """'Запросить статус' недоступна без выбора транзакции."""
        expect(transactions_page.request_status_btn).to_be_disabled()

    def test_send_webhook_disabled_without_selection(self, transactions_page: TransactionsPage):
        """'Отправить вебхук' недоступна без выбора транзакции."""
        expect(transactions_page.send_webhook_btn).to_be_disabled()

    def test_refund_disabled_without_selection(self, transactions_page: TransactionsPage):
        """'Возврат' недоступна без выбора подходящей транзакции."""
        expect(transactions_page.refund_btn).to_be_disabled()


@pytest.mark.ui
class TestRowSelection:
    """Клик по строке не нарушает состояние страницы."""

    def test_clicking_row_keeps_page_loaded(self, transactions_page: TransactionsPage):
        """Клик по строке не вызывает навигацию и страница остаётся загруженной."""
        transactions_page.click_data_row(0)
        # Проверяем, что мы всё ещё на странице транзакций
        assert "/transactions" in transactions_page.page.url

    def test_table_still_has_rows_after_row_click(self, transactions_page: TransactionsPage):
        """После клика по строке таблица всё ещё содержит данные."""
        transactions_page.click_data_row(0)
        assert transactions_page.get_row_count() > 1
