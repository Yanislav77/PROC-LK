"""Тесты страницы логина и логаута: структура, видимость пароля, валидация, выход."""
import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from pages.components.sidebar import Sidebar
from utils.config import TEST_USER_EMAIL, TEST_USER_PASSWORD, BASE_URL


@pytest.fixture
def browser_context_args(browser_context_args):
    # Логин-тесты проверяют форму — убираем storage_state, чтобы стартовать незалогиненным
    return {k: v for k, v in browser_context_args.items() if k != "storage_state"}


@pytest.mark.ui
@pytest.mark.smoke
class TestLoginPageStructure:
    """Структура страницы логина: заголовок, поля, кнопка, ссылки."""

    def test_login_page_title_visible(self, login_page: LoginPage):
        """Заголовок «Вход в личный кабинет» отображается на странице."""
        expect(login_page.title).to_be_visible()

    def test_login_page_title_text(self, login_page: LoginPage):
        """Заголовок страницы содержит точный текст «Вход в личный кабинет»."""
        expect(login_page.title).to_have_text("Вход в личный кабинет")

    def test_username_field_visible(self, login_page: LoginPage):
        """Поле «Логин» отображается на странице."""
        expect(login_page.username_input).to_be_visible()

    def test_username_field_placeholder(self, login_page: LoginPage):
        """Поле «Логин» имеет плейсхолдер «Введите логин»."""
        expect(login_page.username_input).to_have_attribute("placeholder", "Введите логин")

    def test_password_field_visible(self, login_page: LoginPage):
        """Поле «Пароль» отображается на странице."""
        expect(login_page.password_input).to_be_visible()

    def test_password_field_placeholder(self, login_page: LoginPage):
        """Поле «Пароль» имеет плейсхолдер «Введите пароль»."""
        expect(login_page.password_input).to_have_attribute("placeholder", "Введите пароль")

    def test_password_hidden_by_default(self, login_page: LoginPage):
        """Пароль скрыт по умолчанию — тип поля «password»."""
        expect(login_page.password_input).to_have_attribute("type", "password")

    def test_submit_button_visible(self, login_page: LoginPage):
        """Кнопка «Войти» отображается на странице."""
        expect(login_page.submit_btn).to_be_visible()

    def test_submit_button_text(self, login_page: LoginPage):
        """Кнопка входа содержит текст «Войти»."""
        expect(login_page.submit_btn).to_have_text("Войти")

    def test_toggle_password_btn_visible(self, login_page: LoginPage):
        """Иконка показа/скрытия пароля (глаз) отображается рядом с полем пароля."""
        expect(login_page.toggle_password_btn).to_be_visible()

    def test_forgot_password_link_visible(self, login_page: LoginPage):
        """Ссылка «Забыли пароль?» отображается под кнопкой входа."""
        expect(login_page.forgot_password_link).to_be_visible()


@pytest.mark.ui
class TestLoginPasswordToggle:
    """Переключение видимости пароля через иконку глаза."""

    def test_toggle_shows_password(self, login_page: LoginPage):
        """Нажатие на иконку глаза переключает тип поля пароля с password на text."""
        login_page.password_input.fill("somepassword")
        login_page.toggle_password_btn.click()
        expect(login_page.password_input).to_have_attribute("type", "text")

    def test_toggle_twice_hides_password(self, login_page: LoginPage):
        """Повторное нажатие на иконку глаза возвращает тип поля пароля в password."""
        login_page.password_input.fill("somepassword")
        login_page.toggle_password_btn.click()
        login_page.toggle_password_btn.click()
        expect(login_page.password_input).to_have_attribute("type", "password")


@pytest.mark.ui
class TestLoginMaxLength:
    """Ограничение длины ввода в полях логина и пароля."""

    def test_username_field_has_max_length(self, login_page: LoginPage):
        """Поле «Логин» имеет ограничение по количеству символов (атрибут maxlength)."""
        max_len = login_page.username_input.get_attribute("maxlength")
        assert max_len is not None, "Поле логина не имеет атрибута maxlength"
        assert int(max_len) > 0

    def test_password_field_has_max_length(self, login_page: LoginPage):
        """Поле «Пароль» имеет ограничение по количеству символов (атрибут maxlength)."""
        max_len = login_page.password_input.get_attribute("maxlength")
        assert max_len is not None, "Поле пароля не имеет атрибута maxlength"
        assert int(max_len) > 0


@pytest.mark.ui
@pytest.mark.smoke
class TestLoginAction:
    """Поведение при входе: успешный логин, ошибки при неверных данных."""

    def test_successful_login_redirects_to_dashboard(self, login_page: LoginPage):
        """Успешный вход с верными кредами перенаправляет на /dashboard."""
        login_page.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        login_page.page.wait_for_url("**/dashboard**")
        assert "/new/dashboard" in login_page.page.url

    def test_invalid_credentials_shows_error(self, login_page: LoginPage):
        """Неверные логин и пароль показывают сообщение об ошибке."""
        login_page.login("wrong_user", "wrong_password")
        login_page.page.wait_for_timeout(1500)
        expect(login_page.error_msg).to_be_visible()

    def test_invalid_credentials_error_text(self, login_page: LoginPage):
        """Сообщение об ошибке содержит «Некорректный логин или пароль»."""
        login_page.login("wrong_user", "wrong_password")
        login_page.page.wait_for_timeout(1500)
        expect(login_page.error_msg).to_contain_text("Некорректный логин или пароль")

    def test_invalid_credentials_button_disabled(self, login_page: LoginPage):
        """После неверного входа кнопка «Войти» становится неактивной."""
        login_page.login("wrong_user", "wrong_password")
        login_page.page.wait_for_timeout(1500)
        expect(login_page.submit_btn).to_be_disabled()

    def test_invalid_credentials_stays_on_login_page(self, login_page: LoginPage):
        """После неверного входа пользователь остаётся на странице /login."""
        login_page.login("wrong_user", "wrong_password")
        login_page.page.wait_for_timeout(1500)
        assert "/new/login" in login_page.page.url

    def test_wrong_password_stays_on_login(self, login_page: LoginPage):
        """Верный логин, но неверный пароль — остаёмся на странице /login."""
        login_page.login(TEST_USER_EMAIL, "wrongpassword")
        login_page.page.wait_for_timeout(1500)
        assert "/new/login" in login_page.page.url


@pytest.mark.ui
class TestLogout:
    """Выход из кабинета через кнопку в sidebar."""

    @pytest.fixture
    def sidebar(self, authenticated_page: Page) -> Sidebar:
        return Sidebar(authenticated_page)

    def test_logout_btn_visible(self, sidebar: Sidebar):
        """Кнопка «Выход из кабинета» видна в сайдбаре после авторизации."""
        expect(sidebar.logout_btn).to_be_visible()

    def test_logout_btn_text(self, sidebar: Sidebar):
        """Кнопка выхода содержит текст «Выход из кабинета»."""
        expect(sidebar.logout_btn).to_contain_text("Выход из кабинета")

    def test_logout_redirects_to_login(self, sidebar: Sidebar):
        """Нажатие «Выход из кабинета» перенаправляет на страницу /login."""
        sidebar.logout_btn.click()
        sidebar.page.wait_for_load_state("networkidle")
        assert "/login" in sidebar.page.url

