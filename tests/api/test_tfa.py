"""
Тесты TFA API v4:
- POST /api/v4/auth/tfa  — верификация TFA при входе
- PUT  /api/v4/account/tfa — включение/обновление TFA настроек аккаунта

Ключевое требование: refresh токен возвращается в Set-Cookie заголовке,
а НЕ в теле ответа (в отличие от устаревших v1 эндпоинтов).
"""
import pyotp
import pytest

from api_clients.auth_client import AuthClient
from api_clients.tfa_client import TfaClient
from utils.config import (
    TFA_EXISTING_USER_EMAIL,
    TFA_EXISTING_USER_PASSWORD,
    TFA_EXISTING_USER_SECRET,
    TFA_EXISTING_USER_ID,
)

_TFA_PWD = TFA_EXISTING_USER_PASSWORD


@pytest.fixture
def tfa_access_token():
    """Возвращает 2fa_access токен для пользователя с включённым TFA."""
    client = AuthClient()
    r = client.login(TFA_EXISTING_USER_EMAIL, TFA_EXISTING_USER_PASSWORD)
    assert r.status_code == 200
    data = r.json()["response"]
    assert data.get("need_tfa") is True
    return data["access"]


@pytest.fixture
def full_access_token():
    """Логинится, проходит TFA и возвращает полный access токен."""
    client = AuthClient()
    r = client.login(TFA_EXISTING_USER_EMAIL, TFA_EXISTING_USER_PASSWORD)
    access_2fa = r.json()["response"]["access"]
    tfa_client = TfaClient()
    code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
    r2 = tfa_client.verify_tfa(code, access_2fa)
    assert r2.status_code == 200
    return r2.json()["response"]["access"]


@pytest.mark.api
@pytest.mark.smoke
class TestAuthTfaVerify:
    """POST /api/v4/auth/tfa — верификация TFA-кода при входе."""

    def test_verify_tfa_status_200(self, tfa_access_token):
        """Успешная верификация возвращает статус 200."""
        client = TfaClient()
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        r = client.verify_tfa(code, tfa_access_token)
        assert r.status_code == 200

    def test_verify_tfa_returns_access_token(self, tfa_access_token):
        """Тело ответа содержит access токен."""
        client = TfaClient()
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        r = client.verify_tfa(code, tfa_access_token)
        assert "access" in r.json()["response"]

    def test_verify_tfa_refresh_not_in_body(self, tfa_access_token):
        """Refresh токен НЕ присутствует в теле ответа (только в заголовке)."""
        client = TfaClient()
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        r = client.verify_tfa(code, tfa_access_token)
        assert "refresh" not in r.json()["response"], (
            "refresh токен не должен возвращаться в теле ответа"
        )

    def test_verify_tfa_refresh_in_set_cookie(self, tfa_access_token):
        """Refresh токен возвращается в заголовке Set-Cookie как refreshToken."""
        client = TfaClient()
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        r = client.verify_tfa(code, tfa_access_token)
        assert "refreshToken" in r.headers.get("Set-Cookie", ""), (
            "refreshToken должен быть в Set-Cookie заголовке"
        )

    def test_verify_tfa_cookie_is_httponly(self, tfa_access_token):
        """Cookie с refresh токеном имеет флаг HttpOnly."""
        client = TfaClient()
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        r = client.verify_tfa(code, tfa_access_token)
        assert "HttpOnly" in r.headers.get("Set-Cookie", "")

    def test_verify_tfa_invalid_code_returns_error(self, tfa_access_token):
        """Неверный TOTP-код возвращает статус ошибки."""
        client = TfaClient()
        r = client.verify_tfa("000000", tfa_access_token)
        assert r.status_code in (400, 401)

    def test_verify_tfa_invalid_code_no_cookie(self, tfa_access_token):
        """При неверном коде refresh токен в Set-Cookie не устанавливается."""
        client = TfaClient()
        r = client.verify_tfa("000000", tfa_access_token)
        assert "refreshToken" not in r.headers.get("Set-Cookie", "")

    def test_login_with_tfa_user_returns_need_tfa(self):
        """Логин пользователя с TFA возвращает need_tfa=true и временный токен."""
        client = AuthClient()
        r = client.login(TFA_EXISTING_USER_EMAIL, TFA_EXISTING_USER_PASSWORD)
        assert r.status_code == 200
        data = r.json()["response"]
        assert data.get("need_tfa") is True
        assert "access" in data


@pytest.mark.api
class TestAccountTfaUpdate:
    """PUT /api/v4/account/tfa — обновление TFA настроек аккаунта."""

    def test_update_tfa_status_200(self, full_access_token):
        """PUT /account/tfa с корректным кодом возвращает статус 200."""
        client = TfaClient()
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        r = client.connect_tfa(code, full_access_token)
        assert r.status_code == 200

    def test_update_tfa_returns_access_token(self, full_access_token):
        """Тело ответа PUT /account/tfa содержит новый access токен."""
        client = TfaClient()
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        r = client.connect_tfa(code, full_access_token)
        assert "access" in r.json()["response"]

    def test_update_tfa_refresh_not_in_body(self, full_access_token):
        """Refresh токен НЕ присутствует в теле ответа PUT /account/tfa."""
        client = TfaClient()
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        r = client.connect_tfa(code, full_access_token)
        assert "refresh" not in r.json()["response"], (
            "refresh токен не должен возвращаться в теле ответа"
        )

    def test_update_tfa_refresh_in_set_cookie(self, full_access_token):
        """Refresh токен возвращается в Set-Cookie заголовке PUT /account/tfa."""
        client = TfaClient()
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        r = client.connect_tfa(code, full_access_token)
        assert "refreshToken" in r.headers.get("Set-Cookie", ""), (
            "refreshToken должен быть в Set-Cookie заголовке"
        )

    def test_update_tfa_cookie_is_httponly(self, full_access_token):
        """Cookie PUT /account/tfa имеет флаг HttpOnly."""
        client = TfaClient()
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        r = client.connect_tfa(code, full_access_token)
        assert "HttpOnly" in r.headers.get("Set-Cookie", "")

    def test_update_tfa_invalid_code_returns_error(self, full_access_token):
        """Неверный код при PUT /account/tfa возвращает статус ошибки."""
        client = TfaClient()
        r = client.connect_tfa("000000", full_access_token)
        assert r.status_code in (400, 401)


@pytest.mark.api
class TestTfaInvalidToken:
    """Запросы с невалидным Bearer токеном должны возвращать 401."""

    def test_verify_tfa_with_invalid_token(self):
        """POST /auth/tfa с невалидным Bearer токеном возвращает 401."""
        r = TfaClient().verify_tfa("123456", "invalid_token")
        assert r.status_code == 401

    def test_connect_tfa_with_invalid_token(self):
        """PUT /account/tfa с невалидным Bearer токеном возвращает 401."""
        r = TfaClient().connect_tfa("123456", "invalid_token")
        assert r.status_code == 401

    def test_disable_tfa_with_invalid_token(self):
        """PUT /account/tfa (disable) с невалидным Bearer токеном возвращает 401."""
        r = TfaClient().disable_tfa("123456", "password", "invalid_token")
        assert r.status_code == 401


@pytest.mark.api
class TestAccountTfaDisable:
    """PUT /api/v4/account/tfa с use_tfa=False — отключение TFA."""

    @pytest.fixture(autouse=True)
    def restore_tfa_after(self):
        """После теста восстанавливает use_tfa=True через админку (без TOTP)."""
        from utils.admin_helper import set_use_tfa
        yield
        set_use_tfa(TFA_EXISTING_USER_ID, True)

    def test_disable_tfa_status_200(self, full_access_token):
        """PUT /account/tfa с use_tfa=False возвращает статус 200."""
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        r = TfaClient().disable_tfa(code, _TFA_PWD, full_access_token)
        assert r.status_code == 200

    def test_disable_tfa_returns_access_token(self, full_access_token):
        """После отключения TFA в ответе есть новый access токен."""
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        r = TfaClient().disable_tfa(code, _TFA_PWD, full_access_token)
        assert "access" in r.json()["response"]

    def test_disable_tfa_refresh_in_set_cookie(self, full_access_token):
        """После отключения TFA refresh токен возвращается в Set-Cookie."""
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        r = TfaClient().disable_tfa(code, _TFA_PWD, full_access_token)
        assert "refreshToken" in r.headers.get("Set-Cookie", "")

    def test_after_disable_login_returns_no_need_tfa(self, full_access_token):
        """После отключения TFA логин возвращает need_tfa=False или access напрямую."""
        code = pyotp.TOTP(TFA_EXISTING_USER_SECRET).now()
        TfaClient().disable_tfa(code, _TFA_PWD, full_access_token)
        r = AuthClient().login(TFA_EXISTING_USER_EMAIL, TFA_EXISTING_USER_PASSWORD)
        assert r.status_code == 200
        data = r.json()["response"]
        assert data.get("need_tfa") is not True
