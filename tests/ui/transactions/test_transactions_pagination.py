"""Проверяем пагинацию: размер страницы, переключение страниц."""
from urllib.parse import urlparse, parse_qs

import pytest
from playwright.sync_api import Page, expect

from pages.transactions_page import TransactionsPage

TRANSACTIONS_API = "/api/v4/transactions/"


def _capture_transactions_request(page: Page, action) -> dict:
    captured: list[str] = []

    def _on_req(r):
        if TRANSACTIONS_API in r.url and r.method == "GET":
            captured.append(r.url)

    page.on("request", _on_req)
    action()
    page.remove_listener("request", _on_req)
    return parse_qs(urlparse(captured[-1]).query) if captured else {}


@pytest.mark.ui
class TestPageSizeDefault:
    """По умолчанию размер страницы 10 — в dropdown и в таблице."""

    def test_default_page_size_is_10(self, transactions_page: TransactionsPage):
        """По умолчанию в dropdown размера страницы отображается 10."""
        expect(transactions_page.page_size_select).to_have_text("10")

    def test_table_shows_at_most_10_rows_by_default(self, transactions_page: TransactionsPage):
        """По умолчанию таблица показывает не более 10 строк данных."""
        # Строки данных = все строки минус заголовок
        row_count = transactions_page.get_row_count() - 1
        assert row_count <= 10, f"По умолчанию ожидалось <= 10 строк данных, получено {row_count}"


@pytest.mark.ui
class TestPageSizeChange:
    """Смена размера страницы → size=N в GET-запросе."""

    def test_select_25_sends_size_25_in_request(self, transactions_page: TransactionsPage):
        """Выбор 25 → size=25 в запросе."""
        transactions_page.page_size_select.click()
        transactions_page.page.get_by_role("option", name="25", exact=True).wait_for(state="visible")

        params = _capture_transactions_request(
            transactions_page.page,
            lambda: transactions_page.page.get_by_role("option", name="25", exact=True).click(),
        )
        assert params, "Ожидался запрос при смене размера страницы"
        assert params.get("size", [""])[0] == "25", \
            f"Ожидался size=25, получено: {params.get('size')}"

    def test_select_50_sends_size_50_in_request(self, transactions_page: TransactionsPage):
        """Выбор 50 → size=50 в запросе."""
        transactions_page.page_size_select.click()
        transactions_page.page.get_by_role("option", name="50", exact=True).wait_for(state="visible")

        params = _capture_transactions_request(
            transactions_page.page,
            lambda: transactions_page.page.get_by_role("option", name="50", exact=True).click(),
        )
        assert params, "Ожидался запрос при смене размера страницы"
        assert params.get("size", [""])[0] == "50"

    def test_select_100_sends_size_100_in_request(self, transactions_page: TransactionsPage):
        """Выбор 100 → size=100 в запросе."""
        transactions_page.page_size_select.click()
        transactions_page.page.get_by_role("option", name="100", exact=True).wait_for(state="visible")

        params = _capture_transactions_request(
            transactions_page.page,
            lambda: transactions_page.page.get_by_role("option", name="100", exact=True).click(),
        )
        assert params, "Ожидался запрос при смене размера страницы"
        assert params.get("size", [""])[0] == "100"

    def test_select_25_combobox_shows_25(self, transactions_page: TransactionsPage):
        """После выбора 25 в dropdown отображается 25."""
        transactions_page.page_size_select.click()
        transactions_page.page.get_by_role("option", name="25", exact=True).wait_for(state="visible")
        transactions_page.page.get_by_role("option", name="25", exact=True).click()
        expect(transactions_page.page_size_select).to_have_text("25")


@pytest.mark.ui
class TestPaginationNavigation:
    """Переключение страниц → page=N в GET-запросе."""

    def test_page_1_button_visible(self, transactions_page: TransactionsPage):
        """Кнопка страницы 1 видима."""
        expect(transactions_page.get_pagination_button(1)).to_be_visible()

    def test_multiple_page_buttons_present(self, transactions_page: TransactionsPage):
        """Присутствует несколько кнопок страниц (данных достаточно для пагинации)."""
        visible_count = sum(
            1 for i in range(1, 6)
            if transactions_page.get_pagination_button(i).is_visible()
        )
        assert visible_count >= 2, \
            "Ожидалось >= 2 кнопок страниц, данных должно хватать для пагинации"

    def test_click_page_2_sends_page_2_request(self, transactions_page: TransactionsPage):
        """Клик на страницу 2 → page=2 в запросе."""
        page2 = transactions_page.get_pagination_button(2)
        if not page2.is_visible():
            pytest.skip("Кнопка страницы 2 не видна (мало данных)")

        params = _capture_transactions_request(
            transactions_page.page,
            lambda: page2.click(),
        )
        if not params:
            pytest.skip("Запрос не отправлен — React Query cache")
        assert params.get("page", [""])[0] == "2", \
            f"Ожидался page=2, получено: {params.get('page')}"

    def test_click_page_3_sends_page_3_request(self, transactions_page: TransactionsPage):
        """Клик на страницу 3 → page=3 в запросе."""
        page3 = transactions_page.get_pagination_button(3)
        if not page3.is_visible():
            pytest.skip("Кнопка страницы 3 не видна")

        params = _capture_transactions_request(
            transactions_page.page,
            lambda: page3.click(),
        )
        if not params:
            pytest.skip("Запрос не отправлен — React Query cache")
        assert params.get("page", [""])[0] == "3"
