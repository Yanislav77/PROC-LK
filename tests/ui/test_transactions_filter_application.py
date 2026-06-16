from datetime import datetime, timedelta

import pytest
from playwright.sync_api import expect

from pages.transactions_page import TransactionsPage


@pytest.mark.ui
class TestStatusFilterApplication:
    def test_select_status_option_updates_combobox(self, transactions_page: TransactionsPage):
        """Выбор опции в фильтре Статус обновляет его значение."""
        transactions_page.filter_status_select.click()
        options = transactions_page.page.get_by_role("option")
        options.first.wait_for(state="visible")
        option_text = options.nth(1).inner_text()
        options.nth(1).click()
        expect(transactions_page.filter_status_select).to_have_text(option_text)

    def test_applied_status_stays_selected_after_apply(self, transactions_page: TransactionsPage):
        """После нажатия Применить выбранный статус остаётся в фильтре."""
        transactions_page.filter_status_select.click()
        options = transactions_page.page.get_by_role("option")
        options.first.wait_for(state="visible")
        option_text = options.nth(1).inner_text()
        options.nth(1).click()
        transactions_page.apply_filters()
        expect(transactions_page.filter_status_select).to_have_text(option_text)

    def test_applied_status_filter_is_active(self, transactions_page: TransactionsPage):
        """Выбранный статус сохраняется в фильтре даже после применения."""
        transactions_page.filter_status_select.click()
        options = transactions_page.page.get_by_role("option")
        options.first.wait_for(state="visible")
        option_text = options.nth(1).inner_text()
        options.nth(1).click()
        transactions_page.apply_filters()
        # Фильтр должен оставаться выбранным (не сбрасываться автоматически)
        expect(transactions_page.filter_status_select).to_have_text(option_text)

    def test_clear_resets_status_to_all(self, transactions_page: TransactionsPage):
        """Кнопка Очистить сбрасывает Статус до 'Все'."""
        transactions_page.filter_status_select.click()
        transactions_page.page.get_by_role("option").nth(1).wait_for(state="visible")
        transactions_page.page.get_by_role("option").nth(1).click()
        transactions_page.apply_filters()
        transactions_page.clear_filters()
        expect(transactions_page.filter_status_select).to_have_text("Все")


@pytest.mark.ui
class TestDateFilterApplication:
    def test_date_pickers_are_visible(self, transactions_page: TransactionsPage):
        """Поля диапазона дат отображаются на странице."""
        expect(transactions_page.date_from_input).to_be_visible()
        expect(transactions_page.date_to_input).to_be_visible()

    def test_recent_date_range_shows_transactions(self, transactions_page: TransactionsPage):
        """Диапазон последних 7 дней возвращает строки транзакций."""
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        transactions_page.set_date_range(
            week_ago.strftime("%d.%m.%Y"),
            today.strftime("%d.%m.%Y"),
        )
        transactions_page.apply_filters()
        assert transactions_page.get_row_count() > 1

    def test_future_date_range_shows_no_transactions(self, transactions_page: TransactionsPage):
        """Диапазон дат в будущем (2099) возвращает пустую таблицу."""
        transactions_page.set_date_range("01.01.2099", "31.12.2099")
        transactions_page.apply_filters()
        assert transactions_page.get_row_count() <= 1

    def test_clear_after_future_date_restores_transactions(self, transactions_page: TransactionsPage):
        """После Очистить (с пустой будущей датой) транзакции снова видны."""
        transactions_page.set_date_range("01.01.2099", "31.12.2099")
        transactions_page.apply_filters()
        assert transactions_page.get_row_count() <= 1
        transactions_page.clear_filters()
        transactions_page.rows.first.wait_for(state="visible", timeout=15000)
        assert transactions_page.get_row_count() > 1



@pytest.mark.ui
class TestSearchApplication:
    def test_search_input_retains_value_after_apply(self, transactions_page: TransactionsPage):
        """После Применить введённый текст остаётся в поле поиска."""
        transactions_page.search_input.fill("test")
        transactions_page.apply_filters()
        expect(transactions_page.search_input).to_have_value("test")

    def test_clear_resets_search_input(self, transactions_page: TransactionsPage):
        """Очистить сбрасывает поле поиска."""
        transactions_page.search_input.fill("test")
        transactions_page.apply_filters()
        transactions_page.clear_filters()
        expect(transactions_page.search_input).to_have_value("")

    def test_nonexistent_search_term_returns_no_rows(self, transactions_page: TransactionsPage):
        """Поиск по несуществующему тексту возвращает пустую таблицу."""
        transactions_page.search_input.fill("zzz_nonexistent_xyzzy_12345")
        transactions_page.apply_filters()
        assert transactions_page.get_row_count() <= 1
