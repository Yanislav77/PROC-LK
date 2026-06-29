"""
Тесты v4 API авторизации (PROC-83):
  POST /api/v4/auth/token/         — вход, получение refreshToken через HttpOnly cookie
  POST /api/v4/auth/token/refresh/ — обновление токенов через cookie
  POST /api/v4/auth/logout/        — выход с очисткой cookie

Требования, которые не покрываются автотестами (TestAuthV4CannotTest):
  - Атрибут Secure зависит от переменной окружения COOKIE_SECURE
  - Истечение токенов (15 мин / 7 дней) требует реального ожидания
  - Cookie Path enforcement — браузерное поведение, не API
  - Конфигурация ACCESS_TOKEN_LIFETIME / REFRESH_TOKEN_LIFETIME через env
"""
import requests
import pytest

from api_clients.auth_v4_client import AuthV4Client
from utils.config import TEST_USER_EMAIL, TEST_USER_PASSWORD, API_V4_URL


# ---------------------------------------------------------------------------
# POST /api/v4/auth/token/
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestAuthV4Login:
    """POST /api/v4/auth/token/ — вход и получение токенов."""

    def test_login_status_200(self):
        """Успешный логин возвращает статус 200."""
        r = AuthV4Client().login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert r.status_code == 200

    def test_login_response_message_success(self):
        """Тело ответа содержит message=success."""
        r = AuthV4Client().login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert r.json()["message"] == "success"

    def test_login_response_has_access_token(self):
        """Тело ответа содержит access токен."""
        r = AuthV4Client().login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert "access" in r.json()["response"]

    def test_login_response_has_need_tfa_field(self):
        """Тело ответа содержит поле need_tfa."""
        r = AuthV4Client().login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert "need_tfa" in r.json()["response"]

    def test_login_response_has_forced_tfa_field(self):
        """Тело ответа содержит поле forced_tfa."""
        r = AuthV4Client().login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert "forced_tfa" in r.json()["response"]

    def test_login_refresh_not_in_body(self):
        """Refresh токен НЕ присутствует в теле ответа."""
        r = AuthV4Client().login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert "refresh" not in r.json()["response"], (
            "refreshToken не должен возвращаться в теле ответа"
        )

    def test_login_sets_refresh_cookie(self):
        """Ответ содержит заголовок Set-Cookie с refreshToken."""
        r = AuthV4Client().login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert "refreshToken" in r.headers.get("Set-Cookie", ""), (
            "refreshToken должен быть в Set-Cookie заголовке"
        )

    def test_login_cookie_is_httponly(self):
        """Cookie с refresh токеном имеет флаг HttpOnly."""
        r = AuthV4Client().login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert "HttpOnly" in r.headers.get("Set-Cookie", "")

    def test_login_cookie_samesite_lax(self):
        """Cookie имеет атрибут SameSite=Lax."""
        r = AuthV4Client().login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert "SameSite=Lax" in r.headers.get("Set-Cookie", "")

    def test_login_cookie_max_age_7_days(self):
        """Cookie имеет атрибут Max-Age=604800 (7 дней)."""
        r = AuthV4Client().login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert "Max-Age=604800" in r.headers.get("Set-Cookie", "")

    def test_login_cookie_has_path(self):
        """Cookie содержит атрибут Path."""
        r = AuthV4Client().login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert "Path=" in r.headers.get("Set-Cookie", "")

    def test_login_invalid_credentials_returns_error(self):
        """Неверный пароль возвращает статус 400 или 401."""
        r = AuthV4Client().login(TEST_USER_EMAIL, "wrong_password_xyz_12345")
        assert r.status_code in (400, 401)

    def test_login_missing_password_returns_400(self):
        """Отсутствующий пароль возвращает статус 400."""
        r = requests.post(
            f"{API_V4_URL}/auth/token/",
            json={"username": TEST_USER_EMAIL},
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 400

    def test_login_missing_username_returns_400(self):
        """Отсутствующий username возвращает статус 400."""
        r = requests.post(
            f"{API_V4_URL}/auth/token/",
            json={"password": TEST_USER_PASSWORD},
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 400

    def test_login_empty_body_returns_400(self):
        """Пустое тело запроса возвращает статус 400."""
        r = requests.post(
            f"{API_V4_URL}/auth/token/",
            json={},
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# POST /api/v4/auth/token/refresh/
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestAuthV4Refresh:
    """POST /api/v4/auth/token/refresh/ — обновление токенов через cookie."""

    @pytest.fixture
    def client_after_login(self):
        client = AuthV4Client()
        r = client.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert r.status_code == 200, f"Логин не удался: {r.text[:200]}"
        return client

    def test_refresh_status_200(self, client_after_login):
        """Refresh с валидным cookie возвращает статус 200."""
        r = client_after_login.refresh()
        assert r.status_code == 200

    def test_refresh_response_message_success(self, client_after_login):
        """Тело ответа содержит message=success."""
        r = client_after_login.refresh()
        assert r.json()["message"] == "success"

    def test_refresh_returns_new_access_token(self, client_after_login):
        """Тело ответа содержит новый access токен."""
        r = client_after_login.refresh()
        assert "access" in r.json()["response"]

    def test_refresh_not_in_body(self, client_after_login):
        """Новый refresh токен НЕ присутствует в теле ответа."""
        r = client_after_login.refresh()
        assert "refresh" not in r.json()["response"], (
            "refreshToken не должен возвращаться в теле ответа"
        )

    def test_refresh_sets_new_cookie(self, client_after_login):
        """Ответ содержит новый refreshToken в Set-Cookie (ротация токенов)."""
        r = client_after_login.refresh()
        assert "refreshToken" in r.headers.get("Set-Cookie", ""), (
            "Новый refreshToken должен быть в Set-Cookie заголовке"
        )

    def test_refresh_new_cookie_differs_from_old(self, client_after_login):
        """После обновления новый refreshToken отличается от старого."""
        old_token = client_after_login.session.cookies.get("refreshToken")
        client_after_login.refresh()
        new_token = client_after_login.session.cookies.get("refreshToken")
        assert old_token != new_token, (
            "Токен должен меняться после каждого refresh (ротация)"
        )

    def test_refresh_without_cookie_returns_401(self):
        """Refresh без cookie возвращает 401."""
        r = requests.post(
            f"{API_V4_URL}/auth/token/refresh/",
            json={},
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 401

    def test_refresh_without_cookie_error_message(self):
        """Refresh без cookie содержит сообщение 'Refresh token not found'."""
        r = requests.post(
            f"{API_V4_URL}/auth/token/refresh/",
            json={},
            headers={"Content-Type": "application/json"},
        )
        assert "Refresh token not found" in str(r.json()), (
            f"Ожидалось 'Refresh token not found' в ответе, получено: {r.json()}"
        )

    def test_refresh_with_invalid_token_returns_401(self):
        """Невалидный refreshToken cookie возвращает 401."""
        r = AuthV4Client().refresh_with_cookie("deliberately.invalid.token.value")
        assert r.status_code == 401

    def test_refresh_with_invalid_token_error_message(self):
        """Невалидный refreshToken возвращает сообщение 'Invalid or expired refresh token'."""
        r = AuthV4Client().refresh_with_cookie("deliberately.invalid.token.value")
        assert "Invalid or expired refresh token" in str(r.json()), (
            f"Ожидалось 'Invalid or expired refresh token', получено: {r.json()}"
        )

    def test_refresh_with_invalid_token_clears_cookie(self):
        """При невалидном токене сервер очищает cookie через Set-Cookie (требование из комментария Полины)."""
        client = AuthV4Client()
        client.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        r = client.refresh_with_cookie("deliberately.invalid.token.value")
        assert r.status_code == 401
        set_cookie = r.headers.get("Set-Cookie", "")
        assert "refreshToken" in set_cookie, (
            "Сервер должен вернуть Set-Cookie для очистки refreshToken при невалидном токене"
        )
        assert "Max-Age=0" in set_cookie, (
            f"При невалидном токене cookie должна очищаться через Max-Age=0. Set-Cookie: {set_cookie}"
        )

    def test_refresh_already_used_token_returns_401(self):
        """Использованный (ротированный) refreshToken возвращает 401."""
        client = AuthV4Client()
        client.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        old_token = client.session.cookies.get("refreshToken")
        assert old_token, "refreshToken должен быть в сессии после логина"
        r1 = client.refresh()
        assert r1.status_code == 200, "Первый refresh должен пройти успешно"
        r2 = client.refresh_with_cookie(old_token)
        assert r2.status_code == 401

    def test_refresh_already_used_token_error_message(self):
        """Использованный токен возвращает сообщение 'Invalid or expired refresh token'."""
        client = AuthV4Client()
        client.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        old_token = client.session.cookies.get("refreshToken")
        assert old_token
        client.refresh()
        r = client.refresh_with_cookie(old_token)
        assert "Invalid or expired refresh token" in str(r.json()), (
            f"Ожидалось 'Invalid or expired refresh token', получено: {r.json()}"
        )


# ---------------------------------------------------------------------------
# POST /api/v4/auth/logout/
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestAuthV4Logout:
    """POST /api/v4/auth/logout/ — выход с очисткой cookie."""

    @pytest.fixture
    def logged_in_client(self):
        client = AuthV4Client()
        r = client.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        assert r.status_code == 200, f"Логин не удался: {r.text[:200]}"
        return client

    def test_logout_status_200(self, logged_in_client):
        """Logout возвращает статус 200."""
        r = logged_in_client.logout()
        assert r.status_code == 200

    def test_logout_response_message_success(self, logged_in_client):
        """Тело ответа содержит message=success."""
        r = logged_in_client.logout()
        assert r.json()["message"] == "success"

    def test_logout_response_body_is_empty_dict(self, logged_in_client):
        """Тело ответа содержит пустой объект response."""
        r = logged_in_client.logout()
        assert r.json()["response"] == {}

    def test_logout_sets_cookie_with_max_age_0(self, logged_in_client):
        """Logout возвращает Set-Cookie с Max-Age=0 для очистки refreshToken."""
        r = logged_in_client.logout()
        set_cookie = r.headers.get("Set-Cookie", "")
        assert "Max-Age=0" in set_cookie, (
            f"Logout должен очищать cookie через Max-Age=0. Set-Cookie: {set_cookie}"
        )

    def test_logout_set_cookie_contains_token_name(self, logged_in_client):
        """Заголовок Set-Cookie при logout содержит имя refreshToken."""
        r = logged_in_client.logout()
        assert "refreshToken" in r.headers.get("Set-Cookie", ""), (
            "Set-Cookie должен содержать refreshToken при logout"
        )

    def test_refresh_fails_after_logout(self, logged_in_client):
        """После logout попытка использовать старый refreshToken возвращает 401."""
        old_token = logged_in_client.session.cookies.get("refreshToken")
        assert old_token, "refreshToken должен быть в сессии до logout"
        logged_in_client.logout()
        r = logged_in_client.refresh_with_cookie(old_token)
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# Что не покрывается автотестами
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestAuthV4CannotTest:
    """
    Требования из PROC-83, которые не могут быть проверены автотестами.
    Тесты помечены как skip — видны в отчёте как напоминание о непокрытых требованиях.
    """

    @pytest.mark.skip(
        reason="[НЕ ТЕСТИРУЕТСЯ] Атрибут Secure зависит от COOKIE_SECURE на сервере: "
               "true для HTTPS/production, false для development/localhost. "
               "Без доступа к серверной конфигурации нельзя гарантировать ожидаемое значение."
    )
    def test_cookie_secure_flag(self):
        pass

    @pytest.mark.skip(
        reason="[НЕ ТЕСТИРУЕТСЯ] Истечение access токена через 15 минут (900 сек). "
               "Проверка требует реального ожидания. "
               "Частичная альтернатива: проверить поле exp в JWT payload вручную."
    )
    def test_access_token_expires_after_15_minutes(self):
        pass

    @pytest.mark.skip(
        reason="[НЕ ТЕСТИРУЕТСЯ] Истечение refresh токена через 7 дней (604800 сек). "
               "Max-Age=604800 проверяется в TestAuthV4Login.test_login_cookie_max_age_7_days, "
               "но фактическое истечение требует ожидания 7 дней."
    )
    def test_refresh_token_expires_after_7_days(self):
        pass

    @pytest.mark.skip(
        reason="[НЕ ТЕСТИРУЕТСЯ] Cookie Path должен ограничивать отправку cookie только до "
               "эндпоинта refresh (требование из комментария Полины Сергей, 01/06/26). "
               "Это браузерное поведение: requests игнорирует Path при отправке cookies, "
               "проверить через API невозможно."
    )
    def test_cookie_path_restricts_to_refresh_endpoint(self):
        pass

    @pytest.mark.skip(
        reason="[НЕ ТЕСТИРУЕТСЯ] Переменная окружения COOKIE_SECURE влияет на наличие атрибута Secure. "
               "Значение для Path планируется вынести в env var (комментарий Полины Сергей, 01/06/26). "
               "Проверка серверной конфигурации через API невозможна."
    )
    def test_cookie_path_via_env_var(self):
        pass

    @pytest.mark.skip(
        reason="[НЕ ТЕСТИРУЕТСЯ] Переменная окружения ACCESS_TOKEN_LIFETIME (по умолчанию 900 сек). "
               "Изменение конфига сервера и проверка поведения через API-тест невозможны "
               "без перезапуска сервера с другим значением."
    )
    def test_access_token_lifetime_env_var(self):
        pass

    @pytest.mark.skip(
        reason="[НЕ ТЕСТИРУЕТСЯ] Переменная окружения REFRESH_TOKEN_LIFETIME (по умолчанию 604800 сек). "
               "Изменение конфига сервера и проверка поведения через API-тест невозможны "
               "без перезапуска сервера с другим значением."
    )
    def test_refresh_token_lifetime_env_var(self):
        pass
