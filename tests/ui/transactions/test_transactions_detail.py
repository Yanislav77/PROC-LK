"""Тесты страницы детализации транзакции: структура, навигация, кнопки действий."""
import pytest
from playwright.sync_api import expect
from pages.transactions_page import TransactionsPage
from pages.transaction_detail_page import TransactionDetailPage


@pytest.mark.ui
class TestTransactionDetail:
    """Страница детализации: заголовок, секции, навигация и кнопки действий."""

    @pytest.fixture
    def detail_page(self, transactions_page: TransactionsPage) -> TransactionDetailPage:
        detail = TransactionDetailPage(transactions_page.page)
        transactions_page.click_transaction(0)
        transactions_page.page.wait_for_load_state("networkidle")
        return detail

    def test_detail_page_is_loaded(self, detail_page: TransactionDetailPage):
        """Страница детализации успешно загружается после перехода по ссылке."""
        assert detail_page.is_loaded()

    def test_detail_page_title(self, detail_page: TransactionDetailPage):
        """Заголовок страницы содержит текст «Детали транзакции»."""
        expect(detail_page.title).to_have_text("Детали транзакции")

    def test_detail_page_has_history_section(self, detail_page: TransactionDetailPage):
        """Секция «История» присутствует на странице детализации."""
        expect(detail_page.section_history).to_be_visible()

    def test_detail_page_has_payment_details_section(self, detail_page: TransactionDetailPage):
        """Секция «Детали платежа» присутствует на странице детализации."""
        expect(detail_page.section_payment_details).to_be_visible()

    def test_detail_page_has_payment_data_section(self, detail_page: TransactionDetailPage):
        """Секция «Данные платежа» присутствует на странице детализации."""
        expect(detail_page.section_payment_data).to_be_visible()

    def test_detail_page_has_back_link(self, detail_page: TransactionDetailPage):
        """Ссылка «Назад» к списку транзакций присутствует на странице."""
        expect(detail_page.back_link).to_be_visible()

    def test_detail_page_back_link_navigates_to_list(self, detail_page: TransactionDetailPage):
        """Нажатие «Назад» возвращает на страницу списка /transactions."""
        detail_page.go_back()
        assert "/new/transactions" in detail_page.page.url
        # убедимся, что это страница списка, а не детализации
        assert detail_page.page.url.rstrip("/").endswith("/transactions")

    def test_detail_page_has_refund_button(self, detail_page: TransactionDetailPage):
        """Кнопка «Возврат» присутствует на странице детализации."""
        expect(detail_page.refund_btn).to_be_visible()

    def test_detail_page_has_send_webhook_button(self, detail_page: TransactionDetailPage):
        """Кнопка «Отправить вебхук» присутствует на странице детализации."""
        expect(detail_page.send_webhook_btn).to_be_visible()
