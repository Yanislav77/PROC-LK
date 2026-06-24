"""
API-тесты дашборда:
  GET  /api/v1/services/filters/currencies/        — список доступных валют
  POST /api/v1/transactions/filters/services/      — список терминалов по партнёрам
  GET  /api/v1/dashboard/charts/statistics/        — KPI-блоки
  GET  /api/v4/dashboard/charts/countries/         — виджет «Страны» (v4)
  GET  /api/v4/dashboard/charts/ps/               — виджет «Платёжные системы» (v4)

Изменения v4 relative to v1 (countries / ps):
  - amount = сумма транзакций  (в v1 было количество)
  - total  = количество         (в v1 была сумма)
  - добавлено поле success_count

Известные баги:
  - POST /api/v1/transactions/filters/services/ возвращает 405 вместо 200 (метод не реализован)
  - GET /api/v1/dashboard/charts/statistics/ — поле {CURRENCY}.tr_success возвращает float вместо str
"""
import pytest

from api_clients.base_client import BaseClient
from api_clients.dashboard_client import DashboardClient
from api_clients.transactions_client import TransactionsClient

# Последние 30 дней от 2026-06-24 — достаточно широкий диапазон для наличия данных
DATE_RANGE = "2026-05-25T00:00:00.000Z,2026-06-24T23:59:59.999Z"
CURRENCY_RUB = "RUB"


def _make_dashboard_client(auth_client) -> DashboardClient:
    token = auth_client.session.headers.get("Authorization", "").removeprefix("Bearer ")
    return DashboardClient(token=token)


def _make_tx_client(auth_client) -> TransactionsClient:
    token = auth_client.session.headers.get("Authorization", "").removeprefix("Bearer ")
    return TransactionsClient(token=token)


# ---------------------------------------------------------------------------
# Общие фикстуры (module scope)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def dashboard(auth_client) -> DashboardClient:
    return _make_dashboard_client(auth_client)


@pytest.fixture(scope="module")
def partner_ids(auth_client) -> list:
    """ID партнёров для передачи в POST /transactions/filters/services/."""
    tx = _make_tx_client(auth_client)
    r = tx.get_filter_partners()
    partners = BaseClient.unwrap(r)
    if not partners:
        return []
    return [p["id"] for p in partners[:5]]


# ---------------------------------------------------------------------------
# GET /api/v1/services/filters/currencies/
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestDashboardFilterCurrencies:
    """Фильтр валют для дашборда."""

    def test_status_200(self, dashboard):
        """Запрос без параметров → 200 OK."""
        r = dashboard.get_filter_currencies()
        assert r.status_code == 200

    def test_message_success(self, dashboard):
        r = dashboard.get_filter_currencies()
        assert r.json().get("message") == "success"

    def test_response_is_list(self, dashboard):
        r = dashboard.get_filter_currencies()
        assert isinstance(BaseClient.unwrap(r), list)

    def test_response_not_empty(self, dashboard):
        r = dashboard.get_filter_currencies()
        assert len(BaseClient.unwrap(r)) > 0

    def test_all_items_are_strings(self, dashboard):
        """Каждый элемент — строка с кодом валюты (ISO 4217)."""
        r = dashboard.get_filter_currencies()
        data = BaseClient.unwrap(r)
        assert all(isinstance(c, str) for c in data)

    def test_contains_rub(self, dashboard):
        """RUB должен присутствовать в списке."""
        r = dashboard.get_filter_currencies()
        assert CURRENCY_RUB in BaseClient.unwrap(r)

    def test_unauthenticated_returns_401(self):
        r = DashboardClient().get_filter_currencies()
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/v1/transactions/filters/services/
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestDashboardFilterServices:
    """Фильтр терминалов для дашборда."""

    def test_status_200(self, dashboard, partner_ids):
        """БАГ: POST /api/v1/transactions/filters/services/ возвращает 405 Method Not Allowed.
        Spec требует POST с телом {"partners": [...]}, но бэкенд метод не реализован."""
        if not partner_ids:
            pytest.skip("нет доступных партнёров")
        r = dashboard.post_filter_services(partner_ids)
        assert r.status_code == 200

    def test_message_success(self, dashboard, partner_ids):
        if not partner_ids:
            pytest.skip("нет доступных партнёров")
        r = dashboard.post_filter_services(partner_ids)
        assert r.json().get("message") == "success"

    def test_response_is_list(self, dashboard, partner_ids):
        if not partner_ids:
            pytest.skip("нет доступных партнёров")
        r = dashboard.post_filter_services(partner_ids)
        assert isinstance(BaseClient.unwrap(r), list)

    def test_response_not_empty(self, dashboard, partner_ids):
        if not partner_ids:
            pytest.skip("нет доступных партнёров")
        r = dashboard.post_filter_services(partner_ids)
        assert len(BaseClient.unwrap(r)) > 0

    def test_item_has_id_field(self, dashboard, partner_ids):
        """Каждый терминал содержит поле id (spec: response[].id)."""
        if not partner_ids:
            pytest.skip("нет доступных партнёров")
        r = dashboard.post_filter_services(partner_ids)
        data = BaseClient.unwrap(r)
        assert "id" in data[0]

    def test_item_has_name_field(self, dashboard, partner_ids):
        """Каждый терминал содержит поле name (spec: response[].name)."""
        if not partner_ids:
            pytest.skip("нет доступных партнёров")
        r = dashboard.post_filter_services(partner_ids)
        data = BaseClient.unwrap(r)
        assert "name" in data[0]

    def test_item_id_is_int(self, dashboard, partner_ids):
        if not partner_ids:
            pytest.skip("нет доступных партнёров")
        r = dashboard.post_filter_services(partner_ids)
        data = BaseClient.unwrap(r)
        assert isinstance(data[0]["id"], int)

    def test_item_name_is_str(self, dashboard, partner_ids):
        if not partner_ids:
            pytest.skip("нет доступных партнёров")
        r = dashboard.post_filter_services(partner_ids)
        data = BaseClient.unwrap(r)
        assert isinstance(data[0]["name"], str)

    def test_empty_partners_returns_not_500(self, dashboard):
        """Пустой список партнёров не должен давать 500."""
        r = dashboard.post_filter_services([])
        assert r.status_code != 500

    def test_unauthenticated_returns_401(self, partner_ids):
        r = DashboardClient().post_filter_services(partner_ids or [1])
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/v1/dashboard/charts/statistics/
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestDashboardStatistics:
    """KPI-блоки дашборда."""

    @pytest.fixture(scope="class")
    def stats(self, dashboard):
        r = dashboard.get_statistics(created__range=DATE_RANGE)
        return BaseClient.unwrap(r)

    def test_status_200(self, dashboard):
        """Запрос с created__range → 200."""
        r = dashboard.get_statistics(created__range=DATE_RANGE)
        assert r.status_code == 200

    def test_message_success(self, dashboard):
        r = dashboard.get_statistics(created__range=DATE_RANGE)
        assert r.json().get("message") == "success"

    def test_response_has_count_key(self, stats):
        """В ответе присутствует ключ count."""
        assert "count" in stats

    def test_count_has_total(self, stats):
        """count.total — общее количество транзакций."""
        assert "total" in stats["count"]

    def test_count_has_tr_success(self, stats):
        """count.tr_success — количество успешных транзакций."""
        assert "tr_success" in stats["count"]

    def test_count_total_is_int(self, stats):
        assert isinstance(stats["count"]["total"], int)

    def test_count_tr_success_is_int(self, stats):
        assert isinstance(stats["count"]["tr_success"], int)

    def test_tr_success_lte_total(self, stats):
        """Успешных не больше общего числа."""
        assert stats["count"]["tr_success"] <= stats["count"]["total"]

    def test_with_currency_filter_returns_200(self, dashboard):
        r = dashboard.get_statistics(created__range=DATE_RANGE, currency=CURRENCY_RUB)
        assert r.status_code == 200

    def test_currency_key_present_in_response(self, dashboard):
        """При передаче currency в ответе должен быть блок с этой валютой."""
        r = dashboard.get_statistics(created__range=DATE_RANGE, currency=CURRENCY_RUB)
        data = BaseClient.unwrap(r)
        assert CURRENCY_RUB in data

    def test_currency_block_has_tr_success(self, dashboard):
        """Блок валюты содержит tr_success (оборот)."""
        r = dashboard.get_statistics(created__range=DATE_RANGE, currency=CURRENCY_RUB)
        data = BaseClient.unwrap(r)
        assert "tr_success" in data[CURRENCY_RUB]

    def test_currency_tr_success_is_string(self, dashboard):
        """БАГ: оборот по валюте должен передаваться строкой (денежные суммы в API — str),
        но бэкенд возвращает float. Тест фиксирует это расхождение."""
        r = dashboard.get_statistics(created__range=DATE_RANGE, currency=CURRENCY_RUB)
        data = BaseClient.unwrap(r)
        assert isinstance(data[CURRENCY_RUB]["tr_success"], str)

    def test_with_payment_type_returns_200(self, dashboard):
        r = dashboard.get_statistics(created__range=DATE_RANGE, type="payment")
        assert r.status_code == 200

    def test_with_payout_type_returns_200(self, dashboard):
        r = dashboard.get_statistics(created__range=DATE_RANGE, type="payout")
        assert r.status_code == 200

    def test_unauthenticated_returns_401(self):
        r = DashboardClient().get_statistics(created__range=DATE_RANGE)
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/v4/dashboard/charts/countries/
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestDashboardCountries:
    """Виджет «Страны» (v4). Breaking changes v4: amount=сумма, total=кол-во, +success_count."""

    @pytest.fixture(scope="class")
    def countries(self, dashboard):
        r = dashboard.get_countries(
            created__range=DATE_RANGE, currency=CURRENCY_RUB, type="payment"
        )
        return BaseClient.unwrap(r)

    def test_status_200(self, dashboard):
        """type — обязательный параметр (API возвращает 400 без него)."""
        r = dashboard.get_countries(
            created__range=DATE_RANGE, currency=CURRENCY_RUB, type="payment"
        )
        assert r.status_code == 200

    def test_message_success(self, dashboard):
        r = dashboard.get_countries(
            created__range=DATE_RANGE, currency=CURRENCY_RUB, type="payment"
        )
        assert r.json().get("message") == "success"

    def test_type_param_is_required(self, dashboard):
        """Без type / type__in → 400. Документирует поведение, не отражённое в spec."""
        r = dashboard.get_countries(created__range=DATE_RANGE, currency=CURRENCY_RUB)
        assert r.status_code == 400

    def test_response_is_list(self, countries):
        assert isinstance(countries, list)

    def test_item_has_timestamp_field(self, countries):
        if not countries:
            pytest.skip("нет данных за период")
        assert "timestamp" in countries[0]

    def test_item_has_currency_field(self, countries):
        if not countries:
            pytest.skip("нет данных за период")
        assert "currency" in countries[0]

    def test_item_has_type_field(self, countries):
        if not countries:
            pytest.skip("нет данных за период")
        assert "type" in countries[0]

    def test_item_has_metric_field(self, countries):
        """metric — название страны."""
        if not countries:
            pytest.skip("нет данных за период")
        assert "metric" in countries[0]

    def test_item_has_amount_field(self, countries):
        """amount — сумма транзакций (в v4 изменён смысл: было количество)."""
        if not countries:
            pytest.skip("нет данных за период")
        assert "amount" in countries[0]

    def test_item_has_total_field(self, countries):
        """total — количество транзакций (в v4 изменён смысл: была сумма)."""
        if not countries:
            pytest.skip("нет данных за период")
        assert "total" in countries[0]

    def test_item_has_success_count_field(self, countries):
        """success_count — новое поле в v4, отсутствовало в v1."""
        if not countries:
            pytest.skip("нет данных за период")
        assert "success_count" in countries[0]

    def test_amount_is_string(self, countries):
        """amount — денежная сумма, передаётся строкой (десятичная)."""
        if not countries:
            pytest.skip("нет данных за период")
        assert isinstance(countries[0]["amount"], str)

    def test_total_is_int(self, countries):
        """total — целочисленное количество транзакций."""
        if not countries:
            pytest.skip("нет данных за период")
        assert isinstance(countries[0]["total"], int)

    def test_success_count_is_int(self, countries):
        if not countries:
            pytest.skip("нет данных за период")
        assert isinstance(countries[0]["success_count"], int)

    def test_success_count_lte_total(self, countries):
        """Успешных транзакций не больше общего числа по каждой стране."""
        for item in countries:
            assert item["success_count"] <= item["total"]

    def test_with_payment_type_returns_200(self, dashboard):
        r = dashboard.get_countries(
            created__range=DATE_RANGE, currency=CURRENCY_RUB, type="payment"
        )
        assert r.status_code == 200

    def test_with_payout_type_returns_200(self, dashboard):
        r = dashboard.get_countries(
            created__range=DATE_RANGE, currency=CURRENCY_RUB, type="payout"
        )
        assert r.status_code == 200

    def test_with_service_id_filter(self, dashboard, partner_ids):
        if not partner_ids:
            pytest.skip("нет доступных партнёров")
        r_services = dashboard.post_filter_services(partner_ids)
        if r_services.status_code != 200:
            pytest.skip("БАГ: POST /transactions/filters/services/ недоступен")
        services = BaseClient.unwrap(r_services)
        if not services:
            pytest.skip("нет доступных терминалов")
        service_id = services[0]["id"]
        r = dashboard.get_countries(
            created__range=DATE_RANGE,
            currency=CURRENCY_RUB,
            type="payment",
            service_id__in=service_id,
        )
        assert r.status_code == 200

    def test_unauthenticated_returns_401(self):
        r = DashboardClient().get_countries(
            created__range=DATE_RANGE, currency=CURRENCY_RUB, type="payment"
        )
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/v4/dashboard/charts/ps/
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestDashboardPaymentSystems:
    """Виджет «Платёжные системы» (v4). Breaking changes v4: amount=сумма, total=кол-во, +success_count."""

    @pytest.fixture(scope="class")
    def payment_systems(self, dashboard):
        r = dashboard.get_payment_systems(
            created__range=DATE_RANGE, currency=CURRENCY_RUB, type="payment"
        )
        return BaseClient.unwrap(r)

    def test_status_200(self, dashboard):
        """type — обязательный параметр (API возвращает 400 без него)."""
        r = dashboard.get_payment_systems(
            created__range=DATE_RANGE, currency=CURRENCY_RUB, type="payment"
        )
        assert r.status_code == 200

    def test_message_success(self, dashboard):
        r = dashboard.get_payment_systems(
            created__range=DATE_RANGE, currency=CURRENCY_RUB, type="payment"
        )
        assert r.json().get("message") == "success"

    def test_type_param_is_required(self, dashboard):
        """Без type / type__in → 400. Документирует поведение, не отражённое в spec."""
        r = dashboard.get_payment_systems(created__range=DATE_RANGE, currency=CURRENCY_RUB)
        assert r.status_code == 400

    def test_response_is_list(self, payment_systems):
        assert isinstance(payment_systems, list)

    def test_item_has_timestamp_field(self, payment_systems):
        if not payment_systems:
            pytest.skip("нет данных за период")
        assert "timestamp" in payment_systems[0]

    def test_item_has_currency_field(self, payment_systems):
        if not payment_systems:
            pytest.skip("нет данных за период")
        assert "currency" in payment_systems[0]

    def test_item_has_type_field(self, payment_systems):
        if not payment_systems:
            pytest.skip("нет данных за период")
        assert "type" in payment_systems[0]

    def test_item_has_metric_field(self, payment_systems):
        """metric — название платёжной системы."""
        if not payment_systems:
            pytest.skip("нет данных за период")
        assert "metric" in payment_systems[0]

    def test_item_has_amount_field(self, payment_systems):
        """amount — сумма транзакций (в v4 изменён смысл: было количество)."""
        if not payment_systems:
            pytest.skip("нет данных за период")
        assert "amount" in payment_systems[0]

    def test_item_has_total_field(self, payment_systems):
        """total — количество транзакций (в v4 изменён смысл: была сумма)."""
        if not payment_systems:
            pytest.skip("нет данных за период")
        assert "total" in payment_systems[0]

    def test_item_has_success_count_field(self, payment_systems):
        """success_count — новое поле в v4, отсутствовало в v1."""
        if not payment_systems:
            pytest.skip("нет данных за период")
        assert "success_count" in payment_systems[0]

    def test_amount_is_string(self, payment_systems):
        """amount — денежная сумма, передаётся строкой (десятичная)."""
        if not payment_systems:
            pytest.skip("нет данных за период")
        assert isinstance(payment_systems[0]["amount"], str)

    def test_total_is_int(self, payment_systems):
        """total — целочисленное количество транзакций."""
        if not payment_systems:
            pytest.skip("нет данных за период")
        assert isinstance(payment_systems[0]["total"], int)

    def test_success_count_is_int(self, payment_systems):
        if not payment_systems:
            pytest.skip("нет данных за период")
        assert isinstance(payment_systems[0]["success_count"], int)

    def test_success_count_lte_total(self, payment_systems):
        """Успешных транзакций не больше общего числа по каждой ПС."""
        for item in payment_systems:
            assert item["success_count"] <= item["total"]

    def test_with_payment_type_returns_200(self, dashboard):
        r = dashboard.get_payment_systems(
            created__range=DATE_RANGE, currency=CURRENCY_RUB, type="payment"
        )
        assert r.status_code == 200

    def test_with_payout_type_returns_200(self, dashboard):
        r = dashboard.get_payment_systems(
            created__range=DATE_RANGE, currency=CURRENCY_RUB, type="payout"
        )
        assert r.status_code == 200

    def test_with_service_id_filter(self, dashboard, partner_ids):
        if not partner_ids:
            pytest.skip("нет доступных партнёров")
        r_services = dashboard.post_filter_services(partner_ids)
        if r_services.status_code != 200:
            pytest.skip("БАГ: POST /transactions/filters/services/ недоступен")
        services = BaseClient.unwrap(r_services)
        if not services:
            pytest.skip("нет доступных терминалов")
        service_id = services[0]["id"]
        r = dashboard.get_payment_systems(
            created__range=DATE_RANGE,
            currency=CURRENCY_RUB,
            type="payment",
            service_id__in=service_id,
        )
        assert r.status_code == 200

    def test_unauthenticated_returns_401(self):
        r = DashboardClient().get_payment_systems(
            created__range=DATE_RANGE, currency=CURRENCY_RUB, type="payment"
        )
        assert r.status_code == 401
