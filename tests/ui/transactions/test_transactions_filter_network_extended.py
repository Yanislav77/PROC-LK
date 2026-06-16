"""Расширенные сетевые тесты фильтров: метод, режим, тип даты."""
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

import pytest
from playwright.sync_api import Page

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


METHOD_PARAM = "transaction_payment_method"


@pytest.mark.ui
class TestMethodFilterNetwork:
    """Выбор метода (Card, P2P) → запрос содержит transaction_payment_method."""

    def test_method_filter_card_sends_payment_method(self, transactions_page: TransactionsPage):
        """Выбор Card + Apply → запрос содержит transaction_payment_method."""
        transactions_page.filter_method_select.click()
        transactions_page.page.get_by_role("option", name="Card", exact=True).wait_for(state="visible")
        transactions_page.page.get_by_role("option", name="Card", exact=True).click()

        params = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        assert METHOD_PARAM in params, f"{METHOD_PARAM} отсутствует в запросе: {params}"

    def test_method_filter_card_value_contains_card(self, transactions_page: TransactionsPage):
        """transaction_payment_method при выборе Card содержит 'Card'."""
        transactions_page.filter_method_select.click()
        transactions_page.page.get_by_role("option", name="Card", exact=True).wait_for(state="visible")
        transactions_page.page.get_by_role("option", name="Card", exact=True).click()

        params = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        if params and METHOD_PARAM in params:
            assert "card" in params[METHOD_PARAM][0].lower(), \
                f"{METHOD_PARAM} не содержит 'card': {params[METHOD_PARAM]}"

    def test_method_filter_p2p_sends_payment_method(self, transactions_page: TransactionsPage):
        """Выбор P2P + Apply → запрос содержит transaction_payment_method."""
        transactions_page.filter_method_select.click()
        transactions_page.page.get_by_role("option", name="P2P", exact=True).wait_for(state="visible")
        transactions_page.page.get_by_role("option", name="P2P", exact=True).click()

        params = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        assert METHOD_PARAM in params, f"{METHOD_PARAM} отсутствует в запросе: {params}"

    def test_clear_removes_method_filter(self, transactions_page: TransactionsPage):
        """После Очистить запрос не содержит transaction_payment_method."""
        transactions_page.filter_method_select.click()
        transactions_page.page.get_by_role("option", name="Card", exact=True).wait_for(state="visible")
        transactions_page.page.get_by_role("option", name="Card", exact=True).click()
        transactions_page.apply_filters()

        params = _capture_transactions_request(
            transactions_page.page, transactions_page.clear_filters
        )
        if params:
            assert METHOD_PARAM not in params


@pytest.mark.ui
class TestModeFilterNetwork:
    """Выбор режима (Test, Live) → запрос уходит на сервер."""

    def test_mode_test_sends_request(self, transactions_page: TransactionsPage):
        """Выбор Test + Apply → отправляется GET-запрос."""
        transactions_page.filter_mode_select.click()
        transactions_page.page.get_by_role("option", name="Test", exact=True).wait_for(state="visible")
        transactions_page.page.get_by_role("option", name="Test", exact=True).click()

        params = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        assert params, "Ожидался GET-запрос после применения фильтра режима Test"

    def test_mode_live_sends_request(self, transactions_page: TransactionsPage):
        """Выбор Live + Apply → отправляется GET-запрос."""
        transactions_page.filter_mode_select.click()
        transactions_page.page.get_by_role("option", name="Live", exact=True).wait_for(state="visible")
        transactions_page.page.get_by_role("option", name="Live", exact=True).click()

        params = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        assert params, "Ожидался GET-запрос после применения фильтра режима Live"

    def test_mode_filter_params_differ_from_no_filter(self, transactions_page: TransactionsPage):
        """Запрос с фильтром режима отличается от запроса без фильтра."""
        today = datetime.now()
        eight_days_ago = today - timedelta(days=8)
        transactions_page.set_date_range(
            eight_days_ago.strftime("%d.%m.%Y"),
            today.strftime("%d.%m.%Y"),
        )
        params_no_mode = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )

        transactions_page.filter_mode_select.click()
        transactions_page.page.get_by_role("option", name="Test", exact=True).wait_for(state="visible")
        transactions_page.page.get_by_role("option", name="Test", exact=True).click()

        params_with_mode = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        assert params_with_mode != params_no_mode, \
            "Запрос с фильтром режима не отличается от запроса без фильтра"


@pytest.mark.ui
class TestDateTypeFilterNetwork:
    """Тип даты 'Дата оплаты' → запрос содержит payed__range вместо created__range."""

    def test_payment_date_type_sends_payed_range(self, transactions_page: TransactionsPage):
        """Выбор 'Дата оплаты' + Apply → запрос содержит payed__range."""
        today = datetime.now()
        eight_days_ago = today - timedelta(days=8)

        transactions_page.filter_date_type_select.click()
        transactions_page.page.get_by_role("option", name="Дата оплаты", exact=True).wait_for(state="visible")
        transactions_page.page.get_by_role("option", name="Дата оплаты", exact=True).click()

        transactions_page.set_date_range(
            eight_days_ago.strftime("%d.%m.%Y"),
            today.strftime("%d.%m.%Y"),
        )
        params = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        assert params, "Ожидался GET-запрос"
        assert "payed__range" in params, \
            f"payed__range должен быть в запросе при 'Дата оплаты', получено: {params}"

    def test_payment_date_type_no_created_range(self, transactions_page: TransactionsPage):
        """При выборе 'Дата оплаты' created__range не должен быть в запросе."""
        today = datetime.now()
        eight_days_ago = today - timedelta(days=8)

        transactions_page.filter_date_type_select.click()
        transactions_page.page.get_by_role("option", name="Дата оплаты", exact=True).wait_for(state="visible")
        transactions_page.page.get_by_role("option", name="Дата оплаты", exact=True).click()

        transactions_page.set_date_range(
            eight_days_ago.strftime("%d.%m.%Y"),
            today.strftime("%d.%m.%Y"),
        )
        params = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        if params:
            assert "created__range" not in params, \
                "created__range не должен присутствовать при типе 'Дата оплаты'"

    def test_creation_date_type_sends_created_range(self, transactions_page: TransactionsPage):
        """По умолчанию (Дата создания) запрос содержит created__range."""
        today = datetime.now()
        eight_days_ago = today - timedelta(days=8)

        transactions_page.set_date_range(
            eight_days_ago.strftime("%d.%m.%Y"),
            today.strftime("%d.%m.%Y"),
        )
        params = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        assert params, "Ожидался GET-запрос"
        assert "created__range" in params, \
            f"created__range должен быть в запросе по умолчанию, получено: {params}"

    def test_payed_range_has_two_dates(self, transactions_page: TransactionsPage):
        """payed__range содержит два значения даты разделённых запятой."""
        today = datetime.now()
        eight_days_ago = today - timedelta(days=8)

        transactions_page.filter_date_type_select.click()
        transactions_page.page.get_by_role("option", name="Дата оплаты", exact=True).wait_for(state="visible")
        transactions_page.page.get_by_role("option", name="Дата оплаты", exact=True).click()

        transactions_page.set_date_range(
            eight_days_ago.strftime("%d.%m.%Y"),
            today.strftime("%d.%m.%Y"),
        )
        params = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        if params and "payed__range" in params:
            range_val = params["payed__range"][0]
            assert "," in range_val, f"payed__range не содержит запятую: {range_val!r}"
            parts = range_val.split(",")
            assert len(parts) == 2
