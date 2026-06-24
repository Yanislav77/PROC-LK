"""
Тесты API терминалов (сервисов):
  GET /api/v1/services/{service_id}/  — просмотр терминала
  PUT /api/v1/services/{service_id}/  — обновление терминала

Известные баги (тесты упадут намеренно):
  - GET/PUT без авторизации возвращают 500 вместо 401
  - PUT позволяет изменить поле name, которое должно быть иммутабельным
"""
import pytest

from api_clients.auth_client import AuthClient
from api_clients.services_client import ServicesClient
from utils.config import TEST_USER_EMAIL, TEST_USER_PASSWORD

_REQUIRED_FIELDS = {
    "id", "name", "public_name", "site_url",
    "url_success", "url_error", "url_notify", "return_url",
    "processing_host", "available_balance", "currency_code",
    "is_notify", "notify_content_type",
    "secret_key", "status", "is_test",
    "payments_visible", "podeli_approved",
    "public_key", "receipt_flag", "receipt_version",
    "partner_inn", "partner_short_name", "partner_receipt_sender_email",
}


@pytest.fixture(scope="module")
def auth_token():
    r = AuthClient().login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    assert r.status_code == 200
    return r.json()["response"]["access"]


@pytest.fixture(scope="module")
def services_client(auth_token):
    return ServicesClient(token=auth_token)


@pytest.fixture(scope="module")
def service_id(services_client):
    """Берём ID первого активного терминала из списка."""
    r = services_client.get_terminals_list(status=1, page=1, size=1)
    assert r.status_code == 200
    return r.json()["response"]["results"][0]["id"]


@pytest.fixture
def terminal_snapshot(services_client, service_id):
    """Сохраняет текущие данные терминала и восстанавливает после теста."""
    r = services_client.get_terminal(service_id)
    original = r.json()["response"]
    yield original
    services_client.update_terminal(service_id, _build_payload(original))


# ---------------------------------------------------------------------------
# GET /api/v1/services/{service_id}/
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestTerminalGet:
    """GET /api/v1/services/{id}/ — просмотр деталей терминала."""

    def test_get_terminal_status_200(self, services_client, service_id):
        """GET запрос возвращает статус 200."""
        r = services_client.get_terminal(service_id)
        assert r.status_code == 200

    def test_get_terminal_message_success(self, services_client, service_id):
        """Тело ответа содержит message=success."""
        r = services_client.get_terminal(service_id)
        assert r.json().get("message") == "success"

    def test_get_terminal_required_fields_present(self, services_client, service_id):
        """Ответ содержит все обязательные поля согласно спецификации."""
        r = services_client.get_terminal(service_id)
        data = r.json()["response"]
        missing = _REQUIRED_FIELDS - set(data.keys())
        assert not missing, f"Отсутствуют поля: {missing}"

    def test_get_terminal_id_matches(self, services_client, service_id):
        """Поле id в ответе совпадает с запрошенным service_id."""
        r = services_client.get_terminal(service_id)
        assert r.json()["response"]["id"] == service_id

    def test_get_terminal_name_not_empty(self, services_client, service_id):
        """Поле name не пустое."""
        r = services_client.get_terminal(service_id)
        assert r.json()["response"]["name"]

    def test_get_terminal_secret_key_present(self, services_client, service_id):
        """Поле secret_key присутствует и не пустое."""
        r = services_client.get_terminal(service_id)
        assert r.json()["response"]["secret_key"]

    def test_get_terminal_status_is_int(self, services_client, service_id):
        """Поле status является числом (0 — Деактивирован, 1 — Активен)."""
        r = services_client.get_terminal(service_id)
        assert isinstance(r.json()["response"]["status"], int)

    def test_get_terminal_status_valid_values(self, services_client, service_id):
        """Поле status равно 0 или 1."""
        r = services_client.get_terminal(service_id)
        assert r.json()["response"]["status"] in (0, 1)

    def test_get_terminal_is_test_is_bool(self, services_client, service_id):
        """Поле is_test является булевым (false=Production, true=Test)."""
        r = services_client.get_terminal(service_id)
        assert isinstance(r.json()["response"]["is_test"], bool)

    def test_get_terminal_is_notify_is_bool(self, services_client, service_id):
        """Поле is_notify является булевым значением."""
        r = services_client.get_terminal(service_id)
        assert isinstance(r.json()["response"]["is_notify"], bool)

    def test_get_terminal_available_balance_present(self, services_client, service_id):
        """Поле available_balance присутствует в ответе."""
        r = services_client.get_terminal(service_id)
        assert "available_balance" in r.json()["response"]

    def test_get_terminal_currency_code_present(self, services_client, service_id):
        """Поле currency_code присутствует в ответе."""
        r = services_client.get_terminal(service_id)
        assert r.json()["response"].get("currency_code")

    def test_get_terminal_notify_content_type_valid(self, services_client, service_id):
        """Поле notify_content_type равно 'json' или 'xml'."""
        r = services_client.get_terminal(service_id)
        assert r.json()["response"]["notify_content_type"] in ("json", "xml")

    def test_get_terminal_not_found_returns_404(self, services_client):
        """GET несуществующего терминала возвращает 404."""
        r = services_client.get_terminal(9999999)
        assert r.status_code == 404

    def test_get_terminal_unauthenticated_returns_401(self):
        """GET без авторизации возвращает 401.

        БАГ: сервер возвращает 500 вместо 401.
        """
        r = ServicesClient().get_terminal(7128)
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# PUT /api/v1/services/{service_id}/
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestTerminalUpdate:
    """PUT /api/v1/services/{id}/ — обновление терминала."""

    def test_update_terminal_status_200(self, services_client, service_id, terminal_snapshot):
        """PUT с корректными данными возвращает статус 200."""
        r = services_client.update_terminal(service_id, _build_payload(terminal_snapshot))
        assert r.status_code == 200

    def test_update_terminal_message_success(self, services_client, service_id, terminal_snapshot):
        """PUT ответ содержит message=success."""
        r = services_client.update_terminal(service_id, _build_payload(terminal_snapshot))
        assert r.json().get("message") == "success"

    def test_update_terminal_returns_updated_public_name(
        self, services_client, service_id, terminal_snapshot
    ):
        """PUT возвращает обновлённое значение public_name в теле ответа."""
        new_name = "Тестовое публичное имя QA"
        r = services_client.update_terminal(service_id, _build_payload(terminal_snapshot, public_name=new_name))
        assert r.json()["response"]["public_name"] == new_name

    def test_update_terminal_returns_updated_url_success(
        self, services_client, service_id, terminal_snapshot
    ):
        """PUT возвращает обновлённый url_success в теле ответа."""
        new_url = "https://qa-test.example.com/success"
        r = services_client.update_terminal(service_id, _build_payload(terminal_snapshot, url_success=new_url))
        assert r.json()["response"]["url_success"] == new_url

    def test_update_terminal_returns_updated_url_error(
        self, services_client, service_id, terminal_snapshot
    ):
        """PUT возвращает обновлённый url_error в теле ответа."""
        new_url = "https://qa-test.example.com/error"
        r = services_client.update_terminal(service_id, _build_payload(terminal_snapshot, url_error=new_url))
        assert r.json()["response"]["url_error"] == new_url

    def test_update_terminal_returns_updated_url_notify(
        self, services_client, service_id, terminal_snapshot
    ):
        """PUT возвращает обновлённый url_notify в теле ответа."""
        new_url = "https://qa-test.example.com/notify"
        r = services_client.update_terminal(service_id, _build_payload(terminal_snapshot, url_notify=new_url))
        assert r.json()["response"]["url_notify"] == new_url

    def test_update_terminal_returns_updated_return_url(
        self, services_client, service_id, terminal_snapshot
    ):
        """PUT возвращает обновлённый return_url в теле ответа."""
        new_url = "https://qa-test.example.com/return"
        r = services_client.update_terminal(service_id, _build_payload(terminal_snapshot, return_url=new_url))
        assert r.json()["response"]["return_url"] == new_url

    def test_update_terminal_is_notify_toggle(
        self, services_client, service_id, terminal_snapshot
    ):
        """PUT позволяет переключить is_notify."""
        new_val = not terminal_snapshot["is_notify"]
        r = services_client.update_terminal(service_id, _build_payload(terminal_snapshot, is_notify=new_val))
        assert r.json()["response"]["is_notify"] == new_val

    def test_update_terminal_notify_content_type_xml(
        self, services_client, service_id, terminal_snapshot
    ):
        """PUT позволяет изменить notify_content_type на 'xml'."""
        r = services_client.update_terminal(
            service_id, _build_payload(terminal_snapshot, notify_content_type="xml")
        )
        assert r.json()["response"]["notify_content_type"] == "xml"

    def test_update_terminal_name_is_immutable(
        self, services_client, service_id, terminal_snapshot
    ):
        """PUT с изменённым name не должен менять имя терминала.

        БАГ: сервер принимает изменение name, хотя это поле должно быть иммутабельным
        согласно спецификации («поле name не изменяется — валидация на беке»).
        """
        original_name = terminal_snapshot["name"]
        r = services_client.update_terminal(
            service_id, _build_payload(terminal_snapshot, name="Попытка изменить имя QA")
        )
        assert r.status_code == 200
        assert r.json()["response"]["name"] == original_name, (
            f"Имя терминала изменилось: ожидалось {original_name!r}, "
            f"получено {r.json()['response']['name']!r}"
        )

    def test_update_terminal_missing_required_fields_returns_400(
        self, services_client, service_id
    ):
        """PUT без обязательных полей возвращает 400."""
        r = services_client.update_terminal(service_id, {})
        assert r.status_code == 400

    def test_update_terminal_unauthenticated_returns_401(self, service_id):
        """PUT без авторизации возвращает 401.

        БАГ: сервер возвращает 500 вместо 401.
        """
        r = ServicesClient().update_terminal(service_id, {})
        assert r.status_code == 401

    def test_update_terminal_not_found_returns_404(self, services_client, terminal_snapshot):
        """PUT несуществующего терминала возвращает 404."""
        r = services_client.update_terminal(9999999, _build_payload(terminal_snapshot))
        assert r.status_code == 404


def _build_payload(snapshot: dict, **overrides) -> dict:
    payload = {
        "name": snapshot["name"],
        "public_name": snapshot["public_name"],
        "is_test": snapshot["is_test"],
        "site_url": snapshot["site_url"],
        "url_success": snapshot["url_success"],
        "url_error": snapshot["url_error"],
        "url_notify": snapshot["url_notify"],
        "return_url": snapshot["return_url"],
        "processing_host": snapshot["processing_host"],
        "is_notify": snapshot["is_notify"],
        "notify_content_type": snapshot["notify_content_type"],
        "secret_key": snapshot["secret_key"],
        "podeli_approved": snapshot["podeli_approved"],
    }
    payload.update(overrides)
    return payload
