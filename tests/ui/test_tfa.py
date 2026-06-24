"""Тесты двухфакторной аутентификации: настройка TFA, вход с TOTP, вход без TFA."""
import pyotp
import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from pages.tfa_setup_page import TfaSetupPage
from pages.tfa_login_page import TfaLoginPage
from pages.components.sidebar import Sidebar
from utils.config import (
    TFA_EXISTING_USER_EMAIL,
    TFA_EXISTING_USER_PASSWORD,
    TFA_EXISTING_USER_SECRET,
    TFA_EXISTING_USER_ID,
    TFA_NO_TFA_USER_EMAIL,
    TFA_NO_TFA_USER_PASSWORD,
)


@pytest.fixture
def browser_context_args(browser_context_args):
    return {k: v for k, v in browser_context_args.items() if k != "storage_state"}


@pytest.fixture(scope="class")
def fresh_tfa_setup_user():
    """Создаёт свежего пользователя в админке перед классом TestTfaSetup, удаляет после.

    Scope=class: один пользователь на все тесты класса в рамках одного браузера.
    Последний тест класса (test_setup_with_valid_code) завершает TFA setup —
    поэтому пользователь должен быть свежим для каждого браузера.
    """
    from utils.admin_helper import create_fresh_tfa_user, delete_user
    username, password, user_id = create_fresh_tfa_user()
    yield username, password
    delete_user(user_id)


def _do_login(page: Page, username: str, password: str):
    lp = LoginPage(page)
    lp.open()
    lp.login(username, password)


# ---------------------------------------------------------------------------
# TFA Setup — новый пользователь, первый вход
# ---------------------------------------------------------------------------

@pytest.mark.ui
@pytest.mark.smoke
class TestTfaSetup:
    """Первый вход нового пользователя: экран настройки TFA."""

    @pytest.fixture(autouse=True)
    def go_to_setup(self, page: Page, fresh_tfa_setup_user):
        username, password = fresh_tfa_setup_user
        _do_login(page, username, password)
        page.wait_for_url("**/tfa/setup**")

    def test_setup_page_title_visible(self, page: Page):
        """Заголовок «Подключение двухфакторной аутентификации» отображается."""
        expect(TfaSetupPage(page).title).to_be_visible()

    def test_setup_page_title_text(self, page: Page):
        """Заголовок содержит точный текст «Подключение двухфакторной аутентификации»."""
        expect(TfaSetupPage(page).title).to_have_text("Подключение двухфакторной аутентификации")

    def test_setup_page_instruction_visible(self, page: Page):
        """Инструкция «Отсканируйте QR-код в приложении-аутентификаторе» отображается."""
        expect(TfaSetupPage(page).instruction).to_be_visible()

    def test_setup_qr_visible(self, page: Page):
        """QR-код отображается на странице настройки."""
        expect(TfaSetupPage(page).qr_image).to_be_visible()

    def test_setup_manual_key_label_visible(self, page: Page):
        """Текст «Или введите код вручную» отображается под QR-кодом."""
        expect(TfaSetupPage(page).manual_key_label).to_be_visible()

    def test_setup_page_secret_visible(self, page: Page):
        """На странице настройки отображается TOTP-секрет для ручного ввода."""
        expect(TfaSetupPage(page).secret_text).to_be_visible()

    def test_setup_secret_is_base32(self, page: Page):
        """Секрет на странице является валидной Base32-строкой."""
        setup = TfaSetupPage(page)
        secret = setup.get_secret()
        assert len(secret) >= 16, f"Секрет слишком короткий: {secret!r}"
        valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")
        assert all(c in valid_chars for c in secret), f"Невалидный Base32: {secret}"

    def test_setup_page_code_input_visible(self, page: Page):
        """Поле для ввода 6-значного кода отображается на странице."""
        expect(TfaSetupPage(page).code_input).to_be_visible()

    def test_setup_page_code_input_placeholder(self, page: Page):
        """Поле ввода кода имеет плейсхолдер «Введите код»."""
        expect(TfaSetupPage(page).code_input).to_have_attribute("placeholder", "Введите код")

    def test_setup_page_connect_btn_visible(self, page: Page):
        """Кнопка «Подключить» отображается на странице."""
        expect(TfaSetupPage(page).connect_btn).to_be_visible()

    def test_setup_page_connect_btn_text(self, page: Page):
        """Кнопка подключения содержит текст «Подключить»."""
        expect(TfaSetupPage(page).connect_btn).to_have_text("Подключить")

    def test_setup_page_cancel_btn_visible(self, page: Page):
        """Кнопка «Отменить» отображается на странице."""
        expect(TfaSetupPage(page).cancel_btn).to_be_visible()

    def test_setup_page_cancel_btn_text(self, page: Page):
        """Кнопка отмены содержит текст «Отменить»."""
        expect(TfaSetupPage(page).cancel_btn).to_have_text("Отменить")

    def test_setup_wrong_code_shows_error(self, page: Page):
        """Ввод неверного кода показывает сообщение об ошибке «Неверный код»."""
        setup = TfaSetupPage(page)
        setup.submit_code("000000")
        page.wait_for_timeout(1500)
        expect(setup.error_msg).to_be_visible()

    def test_setup_wrong_code_error_text(self, page: Page):
        """Сообщение об ошибке содержит текст «Неверный код»."""
        setup = TfaSetupPage(page)
        setup.submit_code("000000")
        page.wait_for_timeout(1500)
        expect(setup.error_msg).to_have_text("Неверный код")

    def test_setup_cancel_btn_redirects_to_login(self, page: Page):
        """Клик «Отменить» на странице настройки TFA перенаправляет на страницу входа."""
        TfaSetupPage(page).cancel_btn.click()
        page.wait_for_url("**/login**", timeout=10000)
        assert "/login" in page.url

    def test_setup_with_valid_code_redirects_to_dashboard(self, page: Page):
        """Ввод корректного TOTP-кода завершает настройку и перенаправляет на /dashboard."""
        setup = TfaSetupPage(page)
        secret = setup.get_secret()
        code = pyotp.TOTP(secret).now()
        setup.submit_code(code)
        page.wait_for_url("**/dashboard**", timeout=10000)
        assert "/new/dashboard" in page.url


# ---------------------------------------------------------------------------
# TFA Login — существующий пользователь с настроенным TFA
# ---------------------------------------------------------------------------

@pytest.mark.ui
@pytest.mark.smoke
class TestTfaLogin:
    """Вход пользователя с уже настроенным TFA: экран ввода TOTP-кода."""

    @pytest.fixture(scope="class")
    def login_tfa_user(self):
        """Изолированный пользователь с TFA для всего класса."""
        from utils.admin_helper import create_tfa_enabled_user, delete_user
        email, password, secret, user_id = create_tfa_enabled_user()
        yield {"email": email, "password": password, "secret": secret, "id": user_id}
        delete_user(user_id)

    @pytest.fixture(autouse=True)
    def go_to_tfa_login(self, page: Page, login_tfa_user):
        _do_login(page, login_tfa_user["email"], login_tfa_user["password"])
        page.wait_for_url("**/tfa/verify**", timeout=10000)

    def test_tfa_login_page_title_visible(self, page: Page):
        """Заголовок «Двухфакторная аутентификация» отображается."""
        expect(TfaLoginPage(page).title).to_be_visible()

    def test_tfa_login_page_title_text(self, page: Page):
        """Заголовок содержит точный текст «Двухфакторная аутентификация»."""
        expect(TfaLoginPage(page).title).to_have_text("Двухфакторная аутентификация")

    def test_tfa_login_subtitle_visible(self, page: Page):
        """Подзаголовок «Введите код из приложения-аутентификатора» отображается."""
        expect(TfaLoginPage(page).subtitle).to_be_visible()

    def test_tfa_login_code_input_visible(self, page: Page):
        """Поле для ввода кода отображается на странице."""
        expect(TfaLoginPage(page).code_input).to_be_visible()

    def test_tfa_login_code_input_placeholder(self, page: Page):
        """Поле ввода кода имеет плейсхолдер «Введите код»."""
        expect(TfaLoginPage(page).code_input).to_have_attribute("placeholder", "Введите код")

    def test_tfa_login_submit_btn_visible(self, page: Page):
        """Кнопка «Подтвердить» отображается на странице."""
        expect(TfaLoginPage(page).submit_btn).to_be_visible()

    def test_tfa_login_submit_btn_text(self, page: Page):
        """Кнопка подтверждения содержит текст «Подтвердить»."""
        expect(TfaLoginPage(page).submit_btn).to_have_text("Подтвердить")

    def test_tfa_login_logout_btn_visible(self, page: Page):
        """Кнопка «Выйти» отображается на странице."""
        expect(TfaLoginPage(page).logout_btn).to_be_visible()

    def test_tfa_login_with_valid_code_redirects_to_dashboard(self, page: Page, login_tfa_user):
        """Ввод корректного TOTP-кода перенаправляет на /dashboard."""
        tfa = TfaLoginPage(page)
        code = pyotp.TOTP(login_tfa_user["secret"]).now()
        tfa.submit_code(code)
        page.wait_for_url("**/dashboard**", timeout=10000)
        assert "/new/dashboard" in page.url

    def test_tfa_login_with_invalid_code_shows_error(self, page: Page):
        """Ввод неверного TOTP-кода показывает сообщение об ошибке."""
        tfa = TfaLoginPage(page)
        tfa.submit_code("000000")
        page.wait_for_timeout(1500)
        expect(tfa.error_msg).to_be_visible()

    def test_tfa_login_with_invalid_code_error_text(self, page: Page):
        """Сообщение об ошибке содержит текст «Неверный код»."""
        tfa = TfaLoginPage(page)
        tfa.submit_code("000000")
        page.wait_for_timeout(1500)
        expect(tfa.error_msg).to_have_text("Неверный код")

    def test_tfa_login_with_invalid_code_stays_on_page(self, page: Page):
        """После неверного кода пользователь остаётся на странице /tfa/verify."""
        tfa = TfaLoginPage(page)
        tfa.submit_code("000000")
        page.wait_for_timeout(1500)
        assert "/tfa/verify" in page.url

    def test_tfa_login_logout_btn_redirects_to_login(self, page: Page):
        """Клик «Выйти» на странице /tfa/verify перенаправляет на страницу входа."""
        TfaLoginPage(page).logout_btn.click()
        page.wait_for_url("**/login**", timeout=10000)
        assert "/login" in page.url


# ---------------------------------------------------------------------------
# Вход без TFA
# ---------------------------------------------------------------------------

@pytest.mark.ui
@pytest.mark.smoke
class TestLoginWithoutTfa:
    """Вход пользователя без TFA: прямой редирект на /dashboard без экрана кода."""

    def test_login_without_tfa_redirects_to_dashboard(self, page: Page):
        """Пользователь без TFA после логина попадает сразу на /dashboard."""
        _do_login(page, TFA_NO_TFA_USER_EMAIL, TFA_NO_TFA_USER_PASSWORD)
        page.wait_for_url("**/dashboard**", timeout=10000)
        assert "/new/dashboard" in page.url

    def test_login_without_tfa_no_setup_page(self, page: Page):
        """Пользователь без TFA не попадает на /tfa/setup при входе."""
        _do_login(page, TFA_NO_TFA_USER_EMAIL, TFA_NO_TFA_USER_PASSWORD)
        page.wait_for_load_state("networkidle")
        assert "/tfa/setup" not in page.url

    def test_login_without_tfa_no_verify_page(self, page: Page):
        """Пользователь без TFA не попадает на /tfa/verify при входе."""
        _do_login(page, TFA_NO_TFA_USER_EMAIL, TFA_NO_TFA_USER_PASSWORD)
        page.wait_for_load_state("networkidle")
        assert "/tfa/verify" not in page.url


# ---------------------------------------------------------------------------
# Полный цикл TFA: вход → верификация → логаут → повторный вход → верификация
# ---------------------------------------------------------------------------

@pytest.mark.ui
class TestTfaFullCycle:
    """Полный пользовательский сценарий с TFA: два полных цикла входа и выхода."""

    @pytest.fixture(scope="class")
    def full_cycle_user(self):
        """Свежий пользователь с TFA для полного цикла — изолирован от TFA_EXISTING_USER."""
        from utils.admin_helper import create_tfa_enabled_user, delete_user
        email, password, secret, user_id = create_tfa_enabled_user()
        yield {"email": email, "password": password, "secret": secret}
        delete_user(user_id)

    def test_full_tfa_cycle(self, page: Page, full_cycle_user):
        """Логин → /tfa/verify → TOTP → /dashboard → логаут → /login → повторный логин → /tfa/verify → TOTP → /dashboard."""
        import time
        user = full_cycle_user

        # --- первый вход ---
        _do_login(page, user["email"], user["password"])
        page.wait_for_url("**/tfa/verify**", timeout=10000)
        tfa = TfaLoginPage(page)
        tfa.submit_code(pyotp.TOTP(user["secret"]).now())
        page.wait_for_url("**/dashboard**", timeout=10000)
        assert "/new/dashboard" in page.url

        # --- логаут через сайдбар ---
        Sidebar(page).logout_btn.click()
        page.wait_for_url("**/login**", timeout=10000)
        assert "/login" in page.url

        # Ждём нового TOTP-окна чтобы не использовать тот же код повторно
        remaining = 30 - (time.time() % 30)
        if remaining < 5:
            page.wait_for_timeout(int(remaining * 1000) + 1500)

        # --- повторный вход ---
        lp = LoginPage(page)
        lp.username_input.fill(user["email"])
        lp.password_input.fill(user["password"])
        lp.submit_btn.click()
        page.wait_for_url("**/tfa/verify**", timeout=10000)
        tfa = TfaLoginPage(page)
        tfa.submit_code(pyotp.TOTP(user["secret"]).now())
        page.wait_for_url("**/dashboard**", timeout=10000)
        assert "/new/dashboard" in page.url


# ---------------------------------------------------------------------------
# Прямой переход без авторизации — защита роутов
# ---------------------------------------------------------------------------

@pytest.mark.ui
@pytest.mark.smoke
class TestTfaDirectNavigation:
    """Неаутентифицированный доступ к TFA-страницам должен редиректить на /login."""

    def test_unauthenticated_access_to_tfa_verify(self, page: Page):
        """Прямой переход на /tfa/verify без логина перенаправляет на /login."""
        from pages.base_page import BasePage
        BasePage(page).navigate("/tfa/verify")
        page.wait_for_url("**/login**", timeout=10000)
        assert "/login" in page.url

    def test_unauthenticated_access_to_tfa_setup(self, page: Page):
        """Прямой переход на /tfa/setup без логина перенаправляет на /login."""
        from pages.base_page import BasePage
        BasePage(page).navigate("/tfa/setup")
        page.wait_for_url("**/login**", timeout=10000)
        assert "/login" in page.url


# ---------------------------------------------------------------------------
# Флаг ignore_tfa: пользователь с TFA пропускает шаг верификации
# ---------------------------------------------------------------------------

@pytest.mark.ui
class TestTfaIgnoreFlag:
    """Пользователь с use_tfa=True и ignore_tfa=True логинится напрямую в /dashboard."""

    @pytest.fixture(autouse=True)
    def enable_ignore_tfa(self):
        """Включает ignore_tfa для TFA_EXISTING_USER, восстанавливает после теста."""
        from utils.admin_helper import set_ignore_tfa
        set_ignore_tfa(TFA_EXISTING_USER_ID, True)
        yield
        set_ignore_tfa(TFA_EXISTING_USER_ID, False)

    def test_login_with_ignore_tfa_skips_verify(self, page: Page):
        """При ignore_tfa=True вход идёт напрямую на /dashboard без /tfa/verify."""
        _do_login(page, TFA_EXISTING_USER_EMAIL, TFA_EXISTING_USER_PASSWORD)
        page.wait_for_url("**/dashboard**", timeout=10000)
        assert "/tfa/verify" not in page.url
        assert "/new/dashboard" in page.url

    def test_login_with_ignore_tfa_no_verify_page(self, page: Page):
        """При ignore_tfa=True страница /tfa/verify не показывается."""
        _do_login(page, TFA_EXISTING_USER_EMAIL, TFA_EXISTING_USER_PASSWORD)
        page.wait_for_load_state("networkidle")
        assert "/tfa/verify" not in page.url
