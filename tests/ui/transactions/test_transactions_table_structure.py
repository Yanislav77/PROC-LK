"""Проверяем структуру таблицы транзакций: заголовки, данные в строках."""
import pytest
from playwright.sync_api import expect

from pages.transactions_page import TransactionsPage

EXPECTED_HEADERS = [
    "транзакции",   # ID транзакции
    "заказа",       # ID заказа
    "создания",     # Дата создания
    "оплаты",       # Дата оплаты
    "Терминал",
    "Сумма",
    "Валюта",
    "Статус",
    "Режим",
]

KNOWN_STATUSES = [
    "Processing", "Completed", "Authorized",
    "Waiting action", "Cancelled", "Rejected", "Refunded",
    "Resolved chargeback", "New chargeback",
]


@pytest.mark.ui
class TestTableColumns:
    """Все 10 столбцов таблицы присутствуют в заголовке."""

    def _all_headers_text(self, tp: TransactionsPage) -> str:
        return " ".join(tp.page.locator("[role='columnheader']").all_inner_texts())

    def test_has_at_least_8_columns(self, transactions_page: TransactionsPage):
        """Заголовки содержат не менее 8 ожидаемых ключевых слов."""
        combined = self._all_headers_text(transactions_page).lower()
        found = sum(1 for h in EXPECTED_HEADERS if h.lower() in combined)
        assert found >= 8, f"Найдено {found} из {len(EXPECTED_HEADERS)} ожидаемых столбцов в: {combined[:200]!r}"

    def test_has_transaction_id_column(self, transactions_page: TransactionsPage):
        combined = self._all_headers_text(transactions_page)
        assert "транзакции" in combined.lower()

    def test_has_order_id_column(self, transactions_page: TransactionsPage):
        combined = self._all_headers_text(transactions_page)
        assert "заказа" in combined.lower()

    def test_has_creation_date_column(self, transactions_page: TransactionsPage):
        combined = self._all_headers_text(transactions_page)
        assert "создания" in combined.lower()

    def test_has_payment_date_column(self, transactions_page: TransactionsPage):
        combined = self._all_headers_text(transactions_page)
        assert "оплаты" in combined.lower()

    def test_has_terminal_column(self, transactions_page: TransactionsPage):
        combined = self._all_headers_text(transactions_page)
        assert "терминал" in combined.lower()

    def test_has_amount_column(self, transactions_page: TransactionsPage):
        combined = self._all_headers_text(transactions_page)
        assert "сумма" in combined.lower()

    def test_has_currency_column(self, transactions_page: TransactionsPage):
        combined = self._all_headers_text(transactions_page)
        assert "валюта" in combined.lower()

    def test_has_status_column(self, transactions_page: TransactionsPage):
        combined = self._all_headers_text(transactions_page)
        assert "статус" in combined.lower()

    def test_has_mode_column(self, transactions_page: TransactionsPage):
        combined = self._all_headers_text(transactions_page)
        assert "режим" in combined.lower()


@pytest.mark.ui
class TestTableData:
    """Строки данных содержат корректные статусы, режим, даты и ссылки."""

    def test_first_row_has_recognized_status(self, transactions_page: TransactionsPage):
        """Первая строка данных содержит известный статус."""
        row_text = transactions_page.rows.nth(1).inner_text()
        assert any(s in row_text for s in KNOWN_STATUSES), \
            f"Статус не распознан в строке: {row_text[:120]}"

    def test_first_row_has_test_or_live_mode(self, transactions_page: TransactionsPage):
        """Первая строка данных содержит значение режима Test или Live."""
        row_text = transactions_page.rows.nth(1).inner_text()
        assert "Test" in row_text or "Live" in row_text, \
            f"Режим не найден в строке: {row_text[:120]}"

    def test_rows_have_numeric_ids_in_links(self, transactions_page: TransactionsPage):
        """Ссылки на транзакции содержат числовые идентификаторы."""
        links = transactions_page.transaction_links
        assert links.count() > 0
        for i in range(min(3, links.count())):
            href = links.nth(i).get_attribute("href") or ""
            parts = [p for p in href.split("/") if p.isdigit()]
            assert parts, f"Ссылка {href!r} не содержит числового ID"

    def test_multiple_rows_loaded(self, transactions_page: TransactionsPage):
        """Таблица содержит несколько строк данных (не пустая)."""
        assert transactions_page.get_row_count() > 1

    def test_rows_have_date_values(self, transactions_page: TransactionsPage):
        """Строки данных содержат значения дат в формате дд.мм.гггг."""
        row_text = transactions_page.rows.nth(1).inner_text()
        # Дата в формате "09.06.2026" — точки и 10 символов
        import re
        dates = re.findall(r"\d{2}\.\d{2}\.\d{4}", row_text)
        assert dates, f"Дата не найдена в строке: {row_text[:120]}"
