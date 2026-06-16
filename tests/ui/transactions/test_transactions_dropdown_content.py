"""Проверяем содержимое dropdown-фильтров на странице транзакций."""
import pytest
from playwright.sync_api import expect

from pages.transactions_page import TransactionsPage


def _open_and_get_options(tp: TransactionsPage, select_locator) -> list[str]:
    select_locator.click()
    tp.page.get_by_role("option").first.wait_for(state="visible", timeout=5000)
    texts = [o.inner_text().strip() for o in tp.page.get_by_role("option").all()]
    tp.page.keyboard.press("Escape")
    tp.page.wait_for_timeout(150)
    return texts


@pytest.mark.ui
class TestStatusDropdown:
    """Статус: dropdown открывается и содержит все ожидаемые значения."""

    def test_status_dropdown_opens(self, transactions_page: TransactionsPage):
        """Dropdown статуса открывается без ошибок."""
        transactions_page.filter_status_select.click()
        transactions_page.page.get_by_role("option").first.wait_for(state="visible")
        transactions_page.page.keyboard.press("Escape")

    def test_status_has_processing(self, transactions_page: TransactionsPage):
        """В dropdown статуса есть значение Processing."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_status_select)
        assert "Processing" in texts

    def test_status_has_completed(self, transactions_page: TransactionsPage):
        """В dropdown статуса есть значение Completed."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_status_select)
        assert "Completed" in texts

    def test_status_has_authorized(self, transactions_page: TransactionsPage):
        """В dropdown статуса есть значение Authorized."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_status_select)
        assert "Authorized" in texts

    def test_status_has_waiting_action(self, transactions_page: TransactionsPage):
        """В dropdown статуса есть значение Waiting action."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_status_select)
        assert "Waiting action" in texts

    def test_status_has_cancelled(self, transactions_page: TransactionsPage):
        """В dropdown статуса есть значение Cancelled."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_status_select)
        assert "Cancelled" in texts

    def test_status_has_rejected(self, transactions_page: TransactionsPage):
        """В dropdown статуса есть значение Rejected."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_status_select)
        assert "Rejected" in texts

    def test_status_has_refunded(self, transactions_page: TransactionsPage):
        """В dropdown статуса есть значение Refunded."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_status_select)
        assert "Refunded" in texts

    def test_status_has_all_option(self, transactions_page: TransactionsPage):
        """В dropdown статуса есть значение 'Все' (сброс фильтра)."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_status_select)
        assert "Все" in texts


@pytest.mark.ui
class TestMethodDropdown:
    """Метод оплаты: Card, P2P, APM присутствуют в dropdown."""

    def test_method_dropdown_opens(self, transactions_page: TransactionsPage):
        """Dropdown метода открывается без ошибок."""
        transactions_page.filter_method_select.click()
        transactions_page.page.get_by_role("option").first.wait_for(state="visible")
        transactions_page.page.keyboard.press("Escape")

    def test_method_has_card(self, transactions_page: TransactionsPage):
        """В dropdown метода есть значение Card."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_method_select)
        assert "Card" in texts

    def test_method_has_p2p(self, transactions_page: TransactionsPage):
        """В dropdown метода есть значение P2P."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_method_select)
        assert "P2P" in texts

    def test_method_has_apm(self, transactions_page: TransactionsPage):
        """В dropdown метода есть значение APM."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_method_select)
        assert "APM" in texts

    def test_method_has_all_option(self, transactions_page: TransactionsPage):
        """В dropdown метода есть значение 'Все' (сброс фильтра)."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_method_select)
        assert "Все" in texts


@pytest.mark.ui
class TestModeDropdown:
    """Режим: Test и Live присутствуют, других значений нет."""

    def test_mode_dropdown_opens(self, transactions_page: TransactionsPage):
        """Dropdown режима открывается без ошибок."""
        transactions_page.filter_mode_select.click()
        transactions_page.page.get_by_role("option").first.wait_for(state="visible")
        transactions_page.page.keyboard.press("Escape")

    def test_mode_has_test(self, transactions_page: TransactionsPage):
        """В dropdown режима есть значение Test."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_mode_select)
        assert "Test" in texts

    def test_mode_has_live(self, transactions_page: TransactionsPage):
        """В dropdown режима есть значение Live."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_mode_select)
        assert "Live" in texts

    def test_mode_has_exactly_two_real_options(self, transactions_page: TransactionsPage):
        """Кроме 'Все' в фильтре режима ровно два значения: Test и Live."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_mode_select)
        real = [t for t in texts if t != "Все"]
        assert set(real) == {"Test", "Live"}


@pytest.mark.ui
class TestDateTypeDropdown:
    """Тип даты: ровно два значения — Дата создания и Дата оплаты."""

    def test_date_type_dropdown_opens(self, transactions_page: TransactionsPage):
        """Dropdown типа даты открывается без ошибок."""
        transactions_page.filter_date_type_select.click()
        transactions_page.page.get_by_role("option").first.wait_for(state="visible")
        transactions_page.page.keyboard.press("Escape")

    def test_date_type_has_creation_date(self, transactions_page: TransactionsPage):
        """В dropdown типа даты есть значение 'Дата создания'."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_date_type_select)
        assert "Дата создания" in texts

    def test_date_type_has_payment_date(self, transactions_page: TransactionsPage):
        """В dropdown типа даты есть значение 'Дата оплаты'."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_date_type_select)
        assert "Дата оплаты" in texts

    def test_date_type_has_exactly_two_options(self, transactions_page: TransactionsPage):
        """Dropdown типа даты содержит ровно два варианта (без 'Все')."""
        texts = _open_and_get_options(transactions_page, transactions_page.filter_date_type_select)
        assert len(texts) == 2, f"Ожидалось ровно 2 значения, получено: {texts}"


@pytest.mark.ui
class TestSearchTypeDropdown:
    """Параметр поиска: dropdown содержит ID транзакции, ID заказа, Email и другие."""

    def test_search_type_dropdown_opens(self, transactions_page: TransactionsPage):
        """Dropdown параметра поиска открывается и содержит не менее 5 вариантов."""
        transactions_page.search_type_select.click()
        transactions_page.page.get_by_role("option").first.wait_for(state="visible")
        count = len(transactions_page.page.get_by_role("option").all())
        transactions_page.page.keyboard.press("Escape")
        assert count >= 5

    def test_search_type_has_transaction_id(self, transactions_page: TransactionsPage):
        """В параметрах поиска есть вариант 'ID транзакции'."""
        texts = _open_and_get_options(transactions_page, transactions_page.search_type_select)
        assert "ID транзакции" in texts

    def test_search_type_has_order_id(self, transactions_page: TransactionsPage):
        """В параметрах поиска есть вариант 'ID заказа'."""
        texts = _open_and_get_options(transactions_page, transactions_page.search_type_select)
        assert "ID заказа" in texts

    def test_search_type_has_email(self, transactions_page: TransactionsPage):
        """В параметрах поиска есть вариант 'Email'."""
        texts = _open_and_get_options(transactions_page, transactions_page.search_type_select)
        assert "Email" in texts


@pytest.mark.ui
class TestPageSizeDropdown:
    """Размер страницы: доступны 10, 25, 50, 100; дефолт — 10."""

    def test_page_size_dropdown_opens(self, transactions_page: TransactionsPage):
        """Dropdown размера страницы открывается без ошибок."""
        transactions_page.page_size_select.click()
        transactions_page.page.get_by_role("option").first.wait_for(state="visible")
        transactions_page.page.keyboard.press("Escape")

    def test_page_size_has_10(self, transactions_page: TransactionsPage):
        """В dropdown размера страницы есть вариант 10."""
        texts = _open_and_get_options(transactions_page, transactions_page.page_size_select)
        assert "10" in texts

    def test_page_size_has_25(self, transactions_page: TransactionsPage):
        """В dropdown размера страницы есть вариант 25."""
        texts = _open_and_get_options(transactions_page, transactions_page.page_size_select)
        assert "25" in texts

    def test_page_size_has_50(self, transactions_page: TransactionsPage):
        """В dropdown размера страницы есть вариант 50."""
        texts = _open_and_get_options(transactions_page, transactions_page.page_size_select)
        assert "50" in texts

    def test_page_size_has_100(self, transactions_page: TransactionsPage):
        """В dropdown размера страницы есть вариант 100."""
        texts = _open_and_get_options(transactions_page, transactions_page.page_size_select)
        assert "100" in texts

    def test_page_size_default_is_10(self, transactions_page: TransactionsPage):
        """По умолчанию dropdown размера страницы показывает 10."""
        expect(transactions_page.page_size_select).to_have_text("10")
