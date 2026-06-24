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
)

_TFA_PWD = TFA_EXISTING_USER_PASSWORD


@pytest.mark.api
@pytest.mark.smoke
class TestAuthTfaVerify:
    """POST /api/v4/auth/tfa — верификация TFA-кода при входе."""

    @pytest.fixture
    def isolated_tfa_user(self):
        """Свежий пользователь с TFA на каждый тест — исключает повторное использование TOTP-кода."""
        from utils.admin_helper import create_tfa_enabled_user, delete_user
        email, password, secret, user_id = create_tfa_enabled_user()
        yield {"email": email, "password": password, "secret": secret, "id": user_id}
        delete_user(user_id)

    @pytest.fixture
    def verify_tfa_access_token(self, isolated_tfa_user):
        """2fa_access токен для изолированного пользователя."""
        r = AuthClient().login(isolated_tfa_user["email"], isolated_tfa_user["password"])
        assert r.status_code == 200
        data = r.json()["response"]
        assert data.get("need_tfa") is True
        return data["access"]

    def test_verify_tfa_status_200(self, isolated_tfa_user, verify_tfa_access_token):
        """Успешная верификация возвращает статус 200."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r = TfaClient().verify_tfa(code, verify_tfa_access_token)
        assert r.status_code == 200

    def test_verify_tfa_returns_access_token(self, isolated_tfa_user, verify_tfa_access_token):
        """Тело ответа содержит access токен."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r = TfaClient().verify_tfa(code, verify_tfa_access_token)
        assert "access" in r.json()["response"]

    def test_verify_tfa_refresh_not_in_body(self, isolated_tfa_user, verify_tfa_access_token):
        """Refresh токен НЕ присутствует в теле ответа (только в заголовке)."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r = TfaClient().verify_tfa(code, verify_tfa_access_token)
        assert "refresh" not in r.json()["response"], (
            "refresh токен не должен возвращаться в теле ответа"
        )

    def test_verify_tfa_refresh_in_set_cookie(self, isolated_tfa_user, verify_tfa_access_token):
        """Refresh токен возвращается в заголовке Set-Cookie как refreshToken."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r = TfaClient().verify_tfa(code, verify_tfa_access_token)
        assert "refreshToken" in r.headers.get("Set-Cookie", ""), (
            "refreshToken должен быть в Set-Cookie заголовке"
        )

    def test_verify_tfa_cookie_is_httponly(self, isolated_tfa_user, verify_tfa_access_token):
        """Cookie с refresh токеном имеет флаг HttpOnly."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r = TfaClient().verify_tfa(code, verify_tfa_access_token)
        assert "HttpOnly" in r.headers.get("Set-Cookie", "")

    def test_verify_tfa_invalid_code_returns_error(self, verify_tfa_access_token):
        """Неверный TOTP-код возвращает статус ошибки."""
        r = TfaClient().verify_tfa("000000", verify_tfa_access_token)
        assert r.status_code in (400, 401)

    def test_verify_tfa_invalid_code_no_cookie(self, verify_tfa_access_token):
        """При неверном коде refresh токен в Set-Cookie не устанавливается."""
        r = TfaClient().verify_tfa("000000", verify_tfa_access_token)
        assert "refreshToken" not in r.headers.get("Set-Cookie", "")

    def test_login_with_tfa_user_returns_need_tfa(self):
        """Логин пользователя с TFA возвращает need_tfa=true и временный токен."""
        r = AuthClient().login(TFA_EXISTING_USER_EMAIL, TFA_EXISTING_USER_PASSWORD)
        assert r.status_code == 200
        data = r.json()["response"]
        assert data.get("need_tfa") is True
        assert "access" in data


@pytest.mark.api
class TestAccountTfaUpdate:
    """PUT /api/v4/account/tfa — обновление TFA настроек аккаунта."""

    @pytest.fixture
    def isolated_tfa_user(self):
        """Создаёт свежего пользователя с активным TFA, удаляет после теста."""
        from utils.admin_helper import create_tfa_enabled_user, delete_user
        email, password, secret, user_id = create_tfa_enabled_user()
        yield {"email": email, "password": password, "secret": secret, "id": user_id}
        delete_user(user_id)

    @pytest.fixture
    def update_full_access_token(self, isolated_tfa_user):
        """Логинится и проходит TFA для изолированного пользователя."""
        r = AuthClient().login(isolated_tfa_user["email"], isolated_tfa_user["password"])
        access_2fa = r.json()["response"]["access"]
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r2 = TfaClient().verify_tfa(code, access_2fa)
        assert r2.status_code == 200
        return r2.json()["response"]["access"]

    def test_update_tfa_status_200(self, isolated_tfa_user, update_full_access_token):
        """PUT /account/tfa с корректным кодом возвращает статус 200."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r = TfaClient().connect_tfa(code, update_full_access_token)
        assert r.status_code == 200

    def test_update_tfa_returns_access_token(self, isolated_tfa_user, update_full_access_token):
        """Тело ответа PUT /account/tfa содержит новый access токен."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r = TfaClient().connect_tfa(code, update_full_access_token)
        assert "access" in r.json()["response"]

    def test_update_tfa_refresh_not_in_body(self, isolated_tfa_user, update_full_access_token):
        """Refresh токен НЕ присутствует в теле ответа PUT /account/tfa."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r = TfaClient().connect_tfa(code, update_full_access_token)
        assert "refresh" not in r.json()["response"], (
            "refresh токен не должен возвращаться в теле ответа"
        )

    def test_update_tfa_refresh_in_set_cookie(self, isolated_tfa_user, update_full_access_token):
        """Refresh токен возвращается в Set-Cookie заголовке PUT /account/tfa."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r = TfaClient().connect_tfa(code, update_full_access_token)
        assert "refreshToken" in r.headers.get("Set-Cookie", ""), (
            "refreshToken должен быть в Set-Cookie заголовке"
        )

    def test_update_tfa_cookie_is_httponly(self, isolated_tfa_user, update_full_access_token):
        """Cookie PUT /account/tfa имеет флаг HttpOnly."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r = TfaClient().connect_tfa(code, update_full_access_token)
        assert "HttpOnly" in r.headers.get("Set-Cookie", "")

    def test_update_tfa_invalid_code_returns_error(self, isolated_tfa_user, update_full_access_token):
        """Неверный код при PUT /account/tfa возвращает статус ошибки."""
        r = TfaClient().connect_tfa("000000", update_full_access_token)
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

    @pytest.fixture
    def isolated_tfa_user(self):
        """Создаёт свежего пользователя с активным TFA, удаляет после теста."""
        from utils.admin_helper import create_tfa_enabled_user, delete_user
        email, password, secret, user_id = create_tfa_enabled_user()
        yield {"email": email, "password": password, "secret": secret, "id": user_id}
        delete_user(user_id)

    @pytest.fixture
    def disable_full_access_token(self, isolated_tfa_user):
        """Логинится и проходит TFA для изолированного пользователя."""
        r = AuthClient().login(isolated_tfa_user["email"], isolated_tfa_user["password"])
        access_2fa = r.json()["response"]["access"]
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r2 = TfaClient().verify_tfa(code, access_2fa)
        assert r2.status_code == 200
        return r2.json()["response"]["access"]

    def test_disable_tfa_status_200(self, isolated_tfa_user, disable_full_access_token):
        """PUT /account/tfa с use_tfa=False возвращает статус 200."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r = TfaClient().disable_tfa(code, isolated_tfa_user["password"], disable_full_access_token)
        assert r.status_code == 200

    def test_disable_tfa_returns_access_token(self, isolated_tfa_user, disable_full_access_token):
        """После отключения TFA в ответе есть новый access токен."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r = TfaClient().disable_tfa(code, isolated_tfa_user["password"], disable_full_access_token)
        assert "access" in r.json()["response"]

    def test_disable_tfa_refresh_in_set_cookie(self, isolated_tfa_user, disable_full_access_token):
        """После отключения TFA refresh токен возвращается в Set-Cookie."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        r = TfaClient().disable_tfa(code, isolated_tfa_user["password"], disable_full_access_token)
        assert "refreshToken" in r.headers.get("Set-Cookie", "")

    def test_after_disable_login_returns_no_need_tfa(self, isolated_tfa_user, disable_full_access_token):
        """После отключения TFA логин возвращает need_tfa=False или access напрямую."""
        code = pyotp.TOTP(isolated_tfa_user["secret"]).now()
        TfaClient().disable_tfa(code, isolated_tfa_user["password"], disable_full_access_token)
        r = AuthClient().login(isolated_tfa_user["email"], isolated_tfa_user["password"])
        assert r.status_code == 200
        data = r.json()["response"]
        assert data.get("need_tfa") is not True
