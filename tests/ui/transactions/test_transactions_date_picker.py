"""Проверяем поведение датапикеров: значения по умолчанию, взаимодействие."""
from datetime import datetime, timedelta

import pytest
from playwright.sync_api import expect

from pages.transactions_page import TransactionsPage


@pytest.mark.ui
class TestDatePickerDefaults:
    """По умолчанию 'Дата с' = сегодня−7 дней, 'Дата по' = сегодня."""

    def test_date_from_container_visible(self, transactions_page: TransactionsPage):
        expect(transactions_page.date_from_container).to_be_visible()

    def test_date_to_container_visible(self, transactions_page: TransactionsPage):
        expect(transactions_page.date_to_container).to_be_visible()

    def test_date_from_default_day_matches_7_days_ago(self, transactions_page: TransactionsPage):
        """Поле 'Дата с' по умолчанию показывает день = сегодня - 7 дней."""
        expected_day = (datetime.now() - timedelta(days=7)).strftime("%d")
        container_text = transactions_page.date_from_container.inner_text()
        # Container renders as "дд.\nмм.\nгггг\nДата С"
        assert expected_day in container_text, \
            f"Ожидался день {expected_day!r} в 'Дата с', получено: {container_text!r}"

    def test_date_to_default_day_matches_today(self, transactions_page: TransactionsPage):
        """Поле 'Дата по' по умолчанию показывает сегодняшний день."""
        today_day = datetime.now().strftime("%d")
        container_text = transactions_page.date_to_container.inner_text()
        assert today_day in container_text, \
            f"Ожидался день {today_day!r} в 'Дата по', получено: {container_text!r}"

    def test_date_from_default_year_is_current(self, transactions_page: TransactionsPage):
        """Год в 'Дата с' — текущий год."""
        current_year = str(datetime.now().year)
        container_text = transactions_page.date_from_container.inner_text()
        assert current_year in container_text

    def test_date_to_default_year_is_current(self, transactions_page: TransactionsPage):
        """Год в 'Дата по' — текущий год."""
        current_year = str(datetime.now().year)
        container_text = transactions_page.date_to_container.inner_text()
        assert current_year in container_text


@pytest.mark.ui
class TestDatePickerInteraction:
    """Датапикеры кликабельны, принимают ввод с клавиатуры."""

    def test_date_from_is_clickable(self, transactions_page: TransactionsPage):
        """Поле 'Дата с' кликабельно (не disabled)."""
        transactions_page.date_from_container.click()
        # Нет исключения → OK
        transactions_page.page.keyboard.press("Escape")

    def test_date_to_is_clickable(self, transactions_page: TransactionsPage):
        """Поле 'Дата по' кликабельно (не disabled)."""
        transactions_page.date_to_container.click()
        transactions_page.page.keyboard.press("Escape")

    def test_keyboard_entry_changes_date(self, transactions_page: TransactionsPage):
        """Ввод с клавиатуры изменяет значение даты."""
        future = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
        transactions_page.date_to_container.click()
        transactions_page.page.keyboard.press("Home")
        transactions_page.page.keyboard.type(future.replace(".", ""))
        # Поле всё ещё видимо и значение изменилось
        expect(transactions_page.date_to_container).to_be_visible()
        new_text = transactions_page.date_to_container.inner_text()
        expected_day = future[:2]
        assert expected_day in new_text

    def test_set_date_range_updates_both_fields(self, transactions_page: TransactionsPage):
        """set_date_range() обновляет оба поля дат."""
        today = datetime.now()
        date_from = (today - timedelta(days=3)).strftime("%d.%m.%Y")
        date_to = today.strftime("%d.%m.%Y")
        transactions_page.set_date_range(date_from, date_to)
        from_text = transactions_page.date_from_container.inner_text()
        to_text = transactions_page.date_to_container.inner_text()
        assert date_from[:2] in from_text
        assert date_to[:2] in to_text
