"""Проверяем экспорт транзакций: кнопки CSV/XLSX, POST-запросы."""
from urllib.parse import urlparse

import pytest
from playwright.sync_api import Page, expect

from pages.transactions_page import TransactionsPage


def _capture_post_requests(page: Page, action, wait_ms: int = 2000) -> list[str]:
    """Выполняет action, возвращает список URL всех POST-запросов."""
    captured: list[str] = []

    def _on_req(r):
        if r.method == "POST":
            captured.append(r.url)

    page.on("request", _on_req)
    action()
    page.wait_for_timeout(wait_ms)
    page.remove_listener("request", _on_req)
    return captured


@pytest.mark.ui
class TestExportButtonsUI:
    """Кнопки CSV и XLSX видимы, активны и содержат правильный текст."""

    def test_csv_button_visible(self, transactions_page: TransactionsPage):
        expect(transactions_page.export_csv).to_be_visible()

    def test_xlsx_button_visible(self, transactions_page: TransactionsPage):
        expect(transactions_page.export_xlsx).to_be_visible()

    def test_csv_button_enabled(self, transactions_page: TransactionsPage):
        expect(transactions_page.export_csv).to_be_enabled()

    def test_xlsx_button_enabled(self, transactions_page: TransactionsPage):
        expect(transactions_page.export_xlsx).to_be_enabled()

    def test_csv_button_text_is_csv(self, transactions_page: TransactionsPage):
        expect(transactions_page.export_csv).to_have_text("CSV")

    def test_xlsx_button_text_is_xlsx(self, transactions_page: TransactionsPage):
        expect(transactions_page.export_xlsx).to_have_text("XLSX")


@pytest.mark.ui
class TestExportNetworkRequests:
    """Нажатие CSV/XLSX инициирует POST-запрос на один и тот же endpoint."""

    def test_csv_click_sends_post_request(self, transactions_page: TransactionsPage):
        """Нажатие CSV отправляет POST-запрос на сервер."""
        urls = _capture_post_requests(
            transactions_page.page,
            lambda: transactions_page.export_csv.click(),
        )
        assert urls, "CSV экспорт не отправил POST-запрос"

    def test_xlsx_click_sends_post_request(self, transactions_page: TransactionsPage):
        """Нажатие XLSX отправляет POST-запрос на сервер."""
        urls = _capture_post_requests(
            transactions_page.page,
            lambda: transactions_page.export_xlsx.click(),
        )
        assert urls, "XLSX экспорт не отправил POST-запрос"

    def test_csv_and_xlsx_post_to_same_path(self, transactions_page: TransactionsPage):
        """CSV и XLSX используют один и тот же API endpoint."""
        csv_urls = _capture_post_requests(
            transactions_page.page,
            lambda: transactions_page.export_csv.click(),
        )
        transactions_page.page.wait_for_timeout(500)
        xlsx_urls = _capture_post_requests(
            transactions_page.page,
            lambda: transactions_page.export_xlsx.click(),
        )
        if csv_urls and xlsx_urls:
            csv_path = urlparse(csv_urls[-1]).path
            xlsx_path = urlparse(xlsx_urls[-1]).path
            assert csv_path == xlsx_path, \
                f"CSV идёт на {csv_path!r}, XLSX на {xlsx_path!r}"
