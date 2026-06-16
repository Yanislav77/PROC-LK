"""Проверяем наличие и состояние элементов управления фильтрами, кнопок действий и пагинации."""
import re
import pytest
from playwright.sync_api import expect
from pages.transactions_page import TransactionsPage


@pytest.mark.ui
@pytest.mark.smoke
class TestFilterControls:
    """Видимость меток и контролов фильтров, значения по умолчанию."""

    def test_date_type_filter_label_visible(self, transactions_page: TransactionsPage):
        """Метка фильтра «Дата (тип)» отображается на странице."""
        expect(transactions_page.filter_label_date_type).to_be_visible()

    def test_status_filter_label_visible(self, transactions_page: TransactionsPage):
        """Метка фильтра «Статус» отображается на странице."""
        expect(transactions_page.filter_label_status).to_be_visible()

    def test_method_filter_label_visible(self, transactions_page: TransactionsPage):
        """Метка фильтра «Метод» отображается на странице."""
        expect(transactions_page.filter_label_method).to_be_visible()

    def test_mode_filter_label_visible(self, transactions_page: TransactionsPage):
        """Метка фильтра «Режим» отображается на странице."""
        expect(transactions_page.filter_label_mode).to_be_visible()

    def test_terminal_filter_label_visible(self, transactions_page: TransactionsPage):
        """Метка фильтра «Терминал» отображается на странице."""
        expect(transactions_page.filter_label_terminal).to_be_visible()

    def test_organization_filter_label_visible(self, transactions_page: TransactionsPage):
        """Метка фильтра «Организация» отображается на странице."""
        expect(transactions_page.filter_label_organization).to_be_visible()

    def test_search_input_visible(self, transactions_page: TransactionsPage):
        """Поле поиска отображается на странице."""
        expect(transactions_page.search_input).to_be_visible()

    def test_page_size_default_is_10(self, transactions_page: TransactionsPage):
        """По умолчанию dropdown размера страницы показывает 10."""
        expect(transactions_page.page_size_select).to_have_text("10")

    def test_date_type_default_is_date_created(self, transactions_page: TransactionsPage):
        """По умолчанию тип даты установлен в «Дата создания»."""
        expect(transactions_page.filter_date_type_select).to_have_text("Дата создания")

    def test_status_filter_default_is_all(self, transactions_page: TransactionsPage):
        """По умолчанию фильтр статуса установлен в «Все»."""
        expect(transactions_page.filter_status_select).to_have_text("Все")

    def test_search_type_select_visible(self, transactions_page: TransactionsPage):
        """Dropdown типа поиска (параметры поиска) отображается на странице."""
        expect(transactions_page.search_type_select).to_be_visible()

    def test_search_input_accepts_text(self, transactions_page: TransactionsPage):
        """Поле поиска принимает ввод с клавиатуры и сохраняет значение."""
        transactions_page.search_input.fill("12345")
        expect(transactions_page.search_input).to_have_value("12345")


@pytest.mark.ui
class TestActionButtons:
    """Состояние кнопок действий (Возврат / Вебхук / Статус) в зависимости от выбора строки."""

    def test_action_buttons_disabled_by_default(self, transactions_page: TransactionsPage):
        """Все три кнопки действий недоступны (Mui-disabled), пока не выбрана строка."""
        expect(transactions_page.refund_btn).to_have_class(re.compile(r"Mui-disabled"))
        expect(transactions_page.send_webhook_btn).to_have_class(re.compile(r"Mui-disabled"))
        expect(transactions_page.request_status_btn).to_have_class(re.compile(r"Mui-disabled"))

    def test_select_row_enables_send_webhook(self, transactions_page: TransactionsPage):
        """После клика по строке кнопка «Отправить вебхук» становится активной."""
        transactions_page.click_data_row(0)
        expect(transactions_page.send_webhook_btn).not_to_have_class(re.compile(r"Mui-disabled"))

    def test_refund_button_disabled_for_non_refundable_row(self, transactions_page: TransactionsPage):
        """Кнопка «Возврат» остаётся недоступной для строки без статуса Payment+Completed."""
        transactions_page.click_data_row(0)
        # Возврат доступен только для конкретных статусов; по умолчанию остаётся неактивным
        expect(transactions_page.refund_btn).to_have_class(re.compile(r"Mui-disabled"))

    def test_action_buttons_visible(self, transactions_page: TransactionsPage):
        """Все три кнопки действий видимы на странице независимо от выбора строки."""
        expect(transactions_page.refund_btn).to_be_visible()
        expect(transactions_page.send_webhook_btn).to_be_visible()
        expect(transactions_page.request_status_btn).to_be_visible()


@pytest.mark.ui
class TestPagination:
    """Кнопки страниц видимы и переключение не ломает таблицу."""

    def test_pagination_button_1_visible(self, transactions_page: TransactionsPage):
        """Кнопка первой страницы отображается в блоке пагинации."""
        expect(transactions_page.get_pagination_button(1)).to_be_visible()

    def test_pagination_button_2_visible(self, transactions_page: TransactionsPage):
        """Кнопка второй страницы отображается (данных достаточно для пагинации)."""
        expect(transactions_page.get_pagination_button(2)).to_be_visible()

    def test_click_page_2_keeps_table_rows(self, transactions_page: TransactionsPage):
        """После перехода на страницу 2 таблица не пустеет."""
        transactions_page.get_pagination_button(2).click()
        transactions_page.page.wait_for_load_state("networkidle")
        assert transactions_page.get_row_count() > 0
