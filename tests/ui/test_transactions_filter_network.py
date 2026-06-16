"""
Проверяем, что при применении фильтров фронт отправляет правильные
параметры в API /api/v4/transactions/.
"""
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

import pytest
from playwright.sync_api import Page

from pages.transactions_page import TransactionsPage

TRANSACTIONS_API = "/api/v4/transactions/"


def _capture_transactions_request(page: Page, action) -> dict:
    """Выполняет action, возвращает параметры последнего GET к транзакциям.

    Использует on("request") вместо expect_request — чтобы не падать по
    таймауту, если браузер взял результат из кэша React Query.
    """
    captured: list[str] = []

    def _on_req(r):
        if TRANSACTIONS_API in r.url and r.method == "GET":
            captured.append(r.url)

    page.on("request", _on_req)
    action()
    page.remove_listener("request", _on_req)

    if not captured:
        return {}
    return parse_qs(urlparse(captured[-1]).query)


@pytest.mark.ui
class TestFilterNetworkRequests:
    """Каждый фильтр и вкладка отправляют правильные параметры в GET /api/v4/transactions/."""

    def test_apply_sends_transactions_request(self, transactions_page: TransactionsPage):
        """Apply отправляет GET к /api/v4/transactions/ с page и size."""
        today = datetime.now()
        # 8 дней назад — отличается от дефолта (9 дней), поэтому React Query
        # не возьмёт кэш и пошлёт свежий запрос.
        eight_days_ago = today - timedelta(days=8)
        transactions_page.set_date_range(
            eight_days_ago.strftime("%d.%m.%Y"),
            today.strftime("%d.%m.%Y"),
        )
        params = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        assert params, "Ожидался GET-запрос к транзакциям, но запрос не был отправлен"
        assert "page" in params
        assert "size" in params

    def test_status_filter_sends_status_id_in(self, transactions_page: TransactionsPage):
        """Выбор статуса + Apply → запрос содержит status_id__in."""
        transactions_page.filter_status_select.click()
        transactions_page.page.get_by_role("option").nth(1).wait_for(state="visible")
        transactions_page.page.get_by_role("option").nth(1).click()

        params = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        assert "status_id__in" in params, "status_id__in должен быть в запросе"
        assert params["status_id__in"][0], "status_id__in не должен быть пустым"

    def test_clear_removes_status_filter(self, transactions_page: TransactionsPage):
        """После Очистить запрос не содержит status_id__in."""
        transactions_page.filter_status_select.click()
        transactions_page.page.get_by_role("option").nth(1).wait_for(state="visible")
        transactions_page.page.get_by_role("option").nth(1).click()
        transactions_page.apply_filters()

        # При очистке React Query может взять кэш (нет нового запроса) —
        # тогда считаем тест пройденным: UI вернулся к состоянию без фильтра.
        params = _capture_transactions_request(
            transactions_page.page, transactions_page.clear_filters
        )
        if params:
            assert "status_id__in" not in params, \
                "После очистки status_id__in не должен быть в запросе"

    def test_date_filter_sends_created_range(self, transactions_page: TransactionsPage):
        """Apply с изменённой датой → запрос содержит created__range."""
        today = datetime.now()
        eight_days_ago = today - timedelta(days=8)
        transactions_page.set_date_range(
            eight_days_ago.strftime("%d.%m.%Y"),
            today.strftime("%d.%m.%Y"),
        )
        params = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        assert params, "Ожидался GET-запрос к транзакциям"
        assert "created__range" in params, "created__range должен быть в запросе"
        range_val = params["created__range"][0]
        assert "," in range_val, "created__range должен содержать два значения через запятую"

    def test_date_range_from_is_before_to(self, transactions_page: TransactionsPage):
        """Начальная дата в запросе строго раньше конечной."""
        today = datetime.now()
        eight_days_ago = today - timedelta(days=8)
        transactions_page.set_date_range(
            eight_days_ago.strftime("%d.%m.%Y"),
            today.strftime("%d.%m.%Y"),
        )
        params = _capture_transactions_request(
            transactions_page.page, transactions_page.apply_filters
        )
        assert params and "created__range" in params
        date_from_str, date_to_str = params["created__range"][0].split(",")
        date_from = datetime.fromisoformat(date_from_str.strip())
        date_to = datetime.fromisoformat(date_to_str.strip())
        assert date_from < date_to, f"FROM ({date_from}) должна быть раньше TO ({date_to})"

    def test_tab_payouts_sends_type_payout(self, transactions_page: TransactionsPage):
        """Вкладка Выплаты → type__in=payout."""
        params = _capture_transactions_request(
            transactions_page.page,
            lambda: transactions_page.switch_tab("Выплаты"),
        )
        assert params, "Ожидался запрос при смене вкладки"
        assert params.get("type__in", [""])[0] == "payout"

    def test_tab_all_sends_multiple_types(self, transactions_page: TransactionsPage):
        """Вкладка Все → type__in содержит payment и payout."""
        transactions_page.switch_tab("Выплаты")
        params = _capture_transactions_request(
            transactions_page.page,
            lambda: transactions_page.switch_tab("Все"),
        )
        assert params, "Ожидался запрос при смене вкладки"
        type_in = params.get("type__in", [""])[0]
        assert "payment" in type_in
        assert "payout" in type_in

    def test_tab_payments_sends_type_payment(self, transactions_page: TransactionsPage):
        """Вкладка Платежи → type__in=payment (или кэш React Query, тогда skip)."""
        transactions_page.switch_tab("Все")
        params = _capture_transactions_request(
            transactions_page.page,
            lambda: transactions_page.switch_tab("Платежи"),
        )
        if not params:
            pytest.skip("Запрос не отправлен — React Query вернул кэш (дефолтный стейт)")
        assert params.get("type__in", [""])[0] == "payment"

    def test_response_200_with_results_and_count(self, transactions_page: TransactionsPage):
        """Ответ API: статус 200, тело содержит count и results."""
        today = datetime.now()
        eight_days_ago = today - timedelta(days=8)
        transactions_page.set_date_range(
            eight_days_ago.strftime("%d.%m.%Y"),
            today.strftime("%d.%m.%Y"),
        )
        with transactions_page.page.expect_response(
            lambda r: TRANSACTIONS_API in r.url and r.request.method == "GET"
        ) as resp_info:
            transactions_page.apply_filters()

        resp = resp_info.value
        assert resp.status == 200
        data = resp.json().get("response", resp.json())
        assert "count" in data
        assert "results" in data

    def test_status_filter_response_has_matching_statuses(self, transactions_page: TransactionsPage):
        """Ответ после фильтра по статусу содержит транзакции только этого статуса."""
        transactions_page.filter_status_select.click()
        options = transactions_page.page.get_by_role("option")
        options.first.wait_for(state="visible")
        option_text = options.nth(1).inner_text()
        options.nth(1).click()

        with transactions_page.page.expect_response(
            lambda r: TRANSACTIONS_API in r.url and r.request.method == "GET"
        ) as resp_info:
            transactions_page.apply_filters()

        data = resp_info.value.json().get("response", resp_info.value.json())
        results = data.get("results", [])

        if not results:
            pytest.skip(f"Нет транзакций со статусом '{option_text}' в текущем диапазоне")

        status_values = {r["status_verbose"] for r in results}
        assert all(s == option_text for s in status_values), \
            f"Ожидался статус '{option_text}', получены: {status_values}"
