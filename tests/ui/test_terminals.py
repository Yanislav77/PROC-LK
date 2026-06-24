"""
UI тесты страницы терминалов: список и редактирование.

TestTerminalsList  — список терминалов (/terminals): фильтры, таблица, пагинация.
TestTerminalEdit   — форма редактирования (/terminals/{id}): структура, поля, кнопки.

Тесты TestTerminalEdit упадут, пока фронтенд не реализован
(переход на /terminals/{id} редиректит на /dashboard).
"""
import re
import pytest
from playwright.sync_api import Page, expect

from api_clients.auth_client import AuthClient
from api_clients.services_client import ServicesClient
from pages.terminals_page import TerminalsPage
from pages.terminal_edit_page import TerminalEditPage
from utils.config import BASE_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD


def _ensure_authenticated(page: Page) -> None:
    if "/login" in page.url:
        page.locator("input[name=username]").fill(TEST_USER_EMAIL)
        page.locator("input[name=password]").fill(TEST_USER_PASSWORD)
        page.locator("button[type=submit]").click()
        page.wait_for_url("**/dashboard**")
        page.wait_for_load_state("networkidle")


@pytest.fixture
def terminals_page(page: Page) -> TerminalsPage:
    tp = TerminalsPage(page)
    tp.open()
    page.wait_for_load_state("networkidle")
    _ensure_authenticated(page)
    if "/terminals" not in page.url:
        tp.open()
        page.wait_for_load_state("networkidle")
    tp.rows.first.wait_for(state="visible", timeout=15000)
    return tp


@pytest.fixture
def terminal_edit_page(page: Page, terminals_page: TerminalsPage) -> TerminalEditPage:
    """Переходит на страницу редактирования первого терминала."""
    terminals_page.click_first_terminal_link()
    page.wait_for_url(re.compile(r"/terminals/\d+"), timeout=10000)
    page.wait_for_load_state("networkidle")
    return TerminalEditPage(page)


@pytest.fixture
def terminal_edit_with_restore(page: Page, terminal_edit_page: TerminalEditPage):
    """Edit page + API-снэпшот: восстанавливает данные терминала после теста."""
    match = re.search(r"/terminals/(\d+)", page.url)
    service_id = int(match.group(1))

    token = AuthClient().login(TEST_USER_EMAIL, TEST_USER_PASSWORD).json()["response"]["access"]
    client = ServicesClient(token=token)
    original = client.get_terminal(service_id).json()["response"]

    yield terminal_edit_page, service_id, client

    client.update_terminal(service_id, {
        "name": original["name"],
        "public_name": original["public_name"],
        "is_test": original["is_test"],
        "site_url": original["site_url"],
        "url_success": original["url_success"],
        "url_error": original["url_error"],
        "url_notify": original["url_notify"],
        "return_url": original["return_url"],
        "processing_host": original["processing_host"],
        "is_notify": original["is_notify"],
        "notify_content_type": original["notify_content_type"],
        "secret_key": original["secret_key"],
        "podeli_approved": original["podeli_approved"],
    })


# ---------------------------------------------------------------------------
# Список терминалов
# ---------------------------------------------------------------------------

@pytest.mark.ui
@pytest.mark.smoke
class TestTerminalsList:
    """Страница /terminals: заголовок, фильтры, таблица, пагинация."""

    def test_page_title_visible(self, terminals_page: TerminalsPage):
        """Заголовок «Настройки терминалов» отображается на странице."""
        expect(terminals_page.title).to_be_visible()

    def test_page_title_text(self, terminals_page: TerminalsPage):
        """Заголовок страницы содержит точный текст «Настройки терминалов»."""
        expect(terminals_page.title).to_have_text("Настройки терминалов")

    def test_filter_name_input_visible(self, terminals_page: TerminalsPage):
        """Поле поиска по наименованию отображается."""
        expect(terminals_page.filter_name_input).to_be_visible()

    def test_filter_name_placeholder(self, terminals_page: TerminalsPage):
        """Поле поиска имеет плейсхолдер «Наименование»."""
        expect(terminals_page.filter_name_input).to_have_attribute("placeholder", "Наименование")

    def test_filter_org_visible(self, terminals_page: TerminalsPage):
        """Фильтр «Организация» отображается."""
        expect(terminals_page.filter_org_select).to_be_visible()

    def test_filter_currency_visible(self, terminals_page: TerminalsPage):
        """Фильтр «Валюта» отображается."""
        expect(terminals_page.filter_currency_select).to_be_visible()

    def test_filter_mode_visible(self, terminals_page: TerminalsPage):
        """Фильтр «Режим» отображается."""
        expect(terminals_page.filter_mode_select).to_be_visible()

    def test_filter_status_visible(self, terminals_page: TerminalsPage):
        """Фильтр «Статус» отображается."""
        expect(terminals_page.filter_status_select).to_be_visible()

    def test_filter_status_default_value(self, terminals_page: TerminalsPage):
        """Фильтр «Статус» по умолчанию имеет значение «Активен»."""
        expect(terminals_page.filter_status_select).to_have_text("Активен")

    def test_apply_btn_visible(self, terminals_page: TerminalsPage):
        """Кнопка «Применить» отображается."""
        expect(terminals_page.apply_btn).to_be_visible()

    def test_clear_btn_visible(self, terminals_page: TerminalsPage):
        """Кнопка «Очистить» отображается."""
        expect(terminals_page.clear_btn).to_be_visible()

    def test_table_has_rows(self, terminals_page: TerminalsPage):
        """Таблица содержит строки с данными терминалов."""
        assert terminals_page.get_row_count() > 0

    def test_column_header_contains_id(self, terminals_page: TerminalsPage):
        """Заголовок таблицы содержит колонку ID."""
        expect(terminals_page.column_header).to_contain_text("ID")

    def test_column_header_contains_name(self, terminals_page: TerminalsPage):
        """Заголовок таблицы содержит колонку «Наименование»."""
        expect(terminals_page.column_header).to_contain_text("Наименование")

    def test_column_header_contains_processing_host(self, terminals_page: TerminalsPage):
        """Заголовок таблицы содержит колонку «Хост процессинга»."""
        expect(terminals_page.column_header).to_contain_text("Хост процессинга")

    def test_column_header_contains_balance(self, terminals_page: TerminalsPage):
        """Заголовок таблицы содержит колонку «Доступный выплатной остаток»."""
        expect(terminals_page.column_header).to_contain_text("Доступный выплатной остаток")

    def test_column_header_contains_settings(self, terminals_page: TerminalsPage):
        """Заголовок таблицы содержит колонку «Настройка» (иконка для перехода в редактирование)."""
        expect(terminals_page.column_header).to_contain_text("Настройка")

    def test_column_header_contains_status(self, terminals_page: TerminalsPage):
        """Заголовок таблицы содержит колонку «Статус»."""
        expect(terminals_page.column_header).to_contain_text("Статус")

    def test_column_header_contains_mode(self, terminals_page: TerminalsPage):
        """Заголовок таблицы содержит колонку «Режим»."""
        expect(terminals_page.column_header).to_contain_text("Режим")

    def test_first_row_has_link(self, terminals_page: TerminalsPage):
        """Первая строка таблицы содержит ссылку-шестерёнку на страницу редактирования."""
        link = terminals_page.rows.first.locator("a[href*='/terminals/']").first
        expect(link).to_have_attribute("href", re.compile(r"/new/terminals/\d+"))

    def test_pagination_visible(self, terminals_page: TerminalsPage):
        """Пагинация отображается на странице."""
        expect(terminals_page.page_btn_1).to_be_visible()

    def test_page_size_selector_visible(self, terminals_page: TerminalsPage):
        """Селектор количества записей на странице отображается."""
        expect(terminals_page.page_size_select).to_be_visible()

    def test_page_size_default_is_10(self, terminals_page: TerminalsPage):
        """По умолчанию отображается 10 записей на странице."""
        expect(terminals_page.page_size_select).to_have_text("10")

    def test_filter_by_name_sends_request(self, terminals_page: TerminalsPage, page: Page):
        """Применение фильтра по имени отправляет запрос с параметром name__icontains."""
        requests_log = []
        page.on("request", lambda r: requests_log.append(r.url) if "services" in r.url else None)
        terminals_page.filter_name_input.fill("Liza")
        terminals_page.apply_btn.click()
        page.wait_for_load_state("networkidle")
        assert any("name__icontains=Liza" in u for u in requests_log), (
            "Запрос с name__icontains=Liza не был отправлен"
        )

    def test_clear_btn_resets_name_filter(self, terminals_page: TerminalsPage, page: Page):
        """Кнопка «Очистить» сбрасывает фильтр по имени."""
        terminals_page.filter_name_input.fill("Liza")
        terminals_page.clear_btn.click()
        page.wait_for_load_state("networkidle")
        expect(terminals_page.filter_name_input).to_have_value("")


# ---------------------------------------------------------------------------
# Форма редактирования терминала
# ---------------------------------------------------------------------------

@pytest.mark.ui
class TestTerminalEdit:
    """Форма /terminals/{id}: структура, поля, кнопки.

    Тесты упадут до реализации фронтенда (переход редиректит на /dashboard).
    """

    def test_edit_page_url_contains_terminal_id(
        self, terminal_edit_page: TerminalEditPage, page: Page
    ):
        """URL страницы редактирования содержит ID терминала."""
        assert re.search(r"/terminals/\d+", page.url)

    def test_breadcrumb_list_link_visible(self, terminal_edit_page: TerminalEditPage):
        """Хлебная крошка «Настройки терминалов» отображается."""
        expect(terminal_edit_page.breadcrumb_list).to_be_visible()

    def test_breadcrumb_current_visible(self, terminal_edit_page: TerminalEditPage):
        """Хлебная крошка «Редактирование терминала» отображается (per spec/Figma).

        БАГ: текст «Редактирование терминала» отсутствует на странице.
        """
        expect(terminal_edit_page.breadcrumb_current).to_be_visible()

    def test_back_btn_visible(self, terminal_edit_page: TerminalEditPage):
        """Кнопка «Назад» отображается."""
        expect(terminal_edit_page.back_btn).to_be_visible()

    def test_back_btn_returns_to_list(self, terminal_edit_page: TerminalEditPage, page: Page):
        """Клик «Назад» возвращает на страницу списка терминалов."""
        terminal_edit_page.back_btn.click()
        page.wait_for_url("**/terminals", timeout=10000)
        assert "/terminals" in page.url and "/terminals/" not in page.url

    def test_secret_key_input_visible(self, terminal_edit_page: TerminalEditPage):
        """Поле «Секретный ключ» отображается."""
        expect(terminal_edit_page.secret_key_input).to_be_visible()

    def test_secret_key_is_masked(self, terminal_edit_page: TerminalEditPage):
        """Секретный ключ скрыт за звёздочками (тип поля password)."""
        input_type = terminal_edit_page.secret_key_input.get_attribute("type")
        assert input_type == "password", (
            f"Поле secret_key должно быть type=password, получено: {input_type!r}"
        )

    def test_secret_key_is_readonly(self, terminal_edit_page: TerminalEditPage):
        """Поле «Секретный ключ» недоступно для редактирования."""
        disabled = terminal_edit_page.secret_key_input.get_attribute("disabled")
        readonly = terminal_edit_page.secret_key_input.get_attribute("readonly")
        assert disabled is not None or readonly is not None, (
            "Поле secret_key должно быть disabled или readonly"
        )

    def test_copy_btn_visible(self, terminal_edit_page: TerminalEditPage):
        """Кнопка «Копировать» рядом с секретным ключом отображается."""
        expect(terminal_edit_page.copy_btn).to_be_visible()

    def test_name_input_visible(self, terminal_edit_page: TerminalEditPage):
        """Поле «Имя» отображается как форм-элемент (per Figma: disabled input с badge статуса).

        БАГ: поле name отрендерено как статический <p>-текст, а не disabled input.
        """
        expect(terminal_edit_page.name_input).to_be_visible()

    def test_name_input_is_readonly(self, terminal_edit_page: TerminalEditPage):
        """Поле «Имя» недоступно для редактирования (per spec: «не изменяется»).

        БАГ: input[name=name] отсутствует — поле показано как текст, не как disabled input.
        """
        disabled = terminal_edit_page.name_input.get_attribute("disabled")
        readonly = terminal_edit_page.name_input.get_attribute("readonly")
        assert disabled is not None or readonly is not None, (
            "Поле name должно быть disabled или readonly"
        )

    def test_public_name_input_visible(self, terminal_edit_page: TerminalEditPage):
        """Поле «Публичное имя» отображается."""
        expect(terminal_edit_page.public_name_input).to_be_visible()

    def test_public_name_input_is_editable(self, terminal_edit_page: TerminalEditPage):
        """Поле «Публичное имя» доступно для редактирования."""
        expect(terminal_edit_page.public_name_input).to_be_editable()

    def test_processing_host_input_visible(self, terminal_edit_page: TerminalEditPage):
        """Поле «Хост процессинга» отображается."""
        expect(terminal_edit_page.processing_host_input).to_be_visible()

    def test_processing_host_is_readonly(self, terminal_edit_page: TerminalEditPage):
        """Поле «Хост процессинга» недоступно для редактирования (per spec).

        БАГ: input[name=processing_host] существует, но disabled=false и readonly=false —
        поле доступно для ввода, хотя по спецификации должно быть заблокировано.
        """
        disabled = terminal_edit_page.processing_host_input.get_attribute("disabled")
        readonly = terminal_edit_page.processing_host_input.get_attribute("readonly")
        assert disabled is not None or readonly is not None, (
            "Поле processing_host должно быть disabled или readonly"
        )

    def test_mode_input_visible(self, terminal_edit_page: TerminalEditPage):
        """Поле «Режим» (is_test: Test/Production) отображается."""
        expect(terminal_edit_page.mode_input).to_be_visible()

    def test_mode_is_readonly(self, terminal_edit_page: TerminalEditPage):
        """Поле «Режим» (is_test) недоступно для редактирования (per spec).

        БАГ: Select для is_test не заблокирован — aria-disabled отсутствует,
        пользователь может изменить значение, что противоречит спецификации.
        """
        disabled = terminal_edit_page.mode_input.get_attribute("disabled")
        readonly = terminal_edit_page.mode_input.get_attribute("readonly")
        aria_disabled = terminal_edit_page.mode_input.get_attribute("aria-disabled")
        assert disabled is not None or readonly is not None or aria_disabled == "true", (
            "Поле is_test/Режим должно быть disabled, readonly или aria-disabled=true"
        )

    def test_is_notify_toggle_visible(self, terminal_edit_page: TerminalEditPage):
        """Переключатель/чекбокс «Включить оповещения» отображается."""
        expect(terminal_edit_page.is_notify_toggle).to_be_visible()

    def test_url_success_input_visible(self, terminal_edit_page: TerminalEditPage):
        """Поле «URL успеха» отображается."""
        expect(terminal_edit_page.url_success_input).to_be_visible()

    def test_url_success_is_editable(self, terminal_edit_page: TerminalEditPage):
        """Поле «URL успеха» доступно для редактирования."""
        expect(terminal_edit_page.url_success_input).to_be_editable()

    def test_url_error_input_visible(self, terminal_edit_page: TerminalEditPage):
        """Поле «URL ошибки» отображается."""
        expect(terminal_edit_page.url_error_input).to_be_visible()

    def test_url_error_is_editable(self, terminal_edit_page: TerminalEditPage):
        """Поле «URL ошибки» доступно для редактирования."""
        expect(terminal_edit_page.url_error_input).to_be_editable()

    def test_url_notify_input_visible(self, terminal_edit_page: TerminalEditPage):
        """Поле «URL оповещения» отображается."""
        expect(terminal_edit_page.url_notify_input).to_be_visible()

    def test_url_notify_is_editable(self, terminal_edit_page: TerminalEditPage):
        """Поле «URL оповещения» доступно для редактирования."""
        expect(terminal_edit_page.url_notify_input).to_be_editable()

    def test_return_url_input_visible(self, terminal_edit_page: TerminalEditPage):
        """Поле «URL возврата» отображается."""
        expect(terminal_edit_page.return_url_input).to_be_visible()

    def test_return_url_is_editable(self, terminal_edit_page: TerminalEditPage):
        """Поле «URL возврата» доступно для редактирования."""
        expect(terminal_edit_page.return_url_input).to_be_editable()

    def test_save_btn_visible(self, terminal_edit_page: TerminalEditPage):
        """Кнопка «Сохранить» отображается."""
        expect(terminal_edit_page.save_btn).to_be_visible()

    def test_save_btn_text(self, terminal_edit_page: TerminalEditPage):
        """Кнопка сохранения содержит текст «Сохранить»."""
        expect(terminal_edit_page.save_btn).to_have_text("Сохранить")


# ---------------------------------------------------------------------------
# Сетевые запросы при сохранении
# ---------------------------------------------------------------------------

@pytest.mark.ui
class TestTerminalEditNetwork:
    """Проверка HTTP-запросов, которые фронт отправляет на бэк при сохранении формы."""

    def test_save_sends_put_request(
        self, terminal_edit_with_restore, page: Page
    ):
        """Клик «Сохранить» отправляет PUT /api/v1/services/{id}/."""
        edit_page, service_id, _ = terminal_edit_with_restore
        with page.expect_request(
            lambda r: r.method == "PUT" and f"/services/{service_id}/" in r.url
        ) as req_info:
            edit_page.save_btn.click()
        assert f"/services/{service_id}/" in req_info.value.url

    def test_save_request_contains_public_name(
        self, terminal_edit_with_restore, page: Page
    ):
        """Изменённый public_name попадает в тело PUT-запроса."""
        edit_page, service_id, _ = terminal_edit_with_restore
        new_name = "QA Public Name Test"
        edit_page.public_name_input.fill(new_name)
        with page.expect_request(
            lambda r: r.method == "PUT" and f"/services/{service_id}/" in r.url
        ) as req_info:
            edit_page.save_btn.click()
        assert new_name in (req_info.value.post_data or ""), (
            "Новый public_name не найден в теле PUT-запроса"
        )

    def test_save_request_contains_url_success(
        self, terminal_edit_with_restore, page: Page
    ):
        """Изменённый url_success попадает в тело PUT-запроса."""
        edit_page, service_id, _ = terminal_edit_with_restore
        new_url = "https://qa-ui-test.example.com/success"
        edit_page.url_success_input.fill(new_url)
        with page.expect_request(
            lambda r: r.method == "PUT" and f"/services/{service_id}/" in r.url
        ) as req_info:
            edit_page.save_btn.click()
        assert new_url in (req_info.value.post_data or ""), (
            "Новый url_success не найден в теле PUT-запроса"
        )

    def test_save_request_contains_is_notify(
        self, terminal_edit_with_restore, page: Page
    ):
        """Изменённый is_notify попадает в тело PUT-запроса."""
        edit_page, service_id, client = terminal_edit_with_restore
        current_val = client.get_terminal(service_id).json()["response"]["is_notify"]
        edit_page.is_notify_toggle.click()
        with page.expect_request(
            lambda r: r.method == "PUT" and f"/services/{service_id}/" in r.url
        ) as req_info:
            edit_page.save_btn.click()
        expected = str(not current_val).lower()
        assert expected in (req_info.value.post_data or "").lower(), (
            f"Ожидали is_notify={expected} в теле запроса"
        )

    def test_save_returns_200(
        self, terminal_edit_with_restore, page: Page
    ):
        """PUT при сохранении возвращает статус 200."""
        edit_page, service_id, _ = terminal_edit_with_restore
        responses = []
        page.on(
            "response",
            lambda r: responses.append(r) if f"/services/{service_id}/" in r.url and r.request.method == "PUT" else None,
        )
        edit_page.save_btn.click()
        page.wait_for_load_state("networkidle")
        assert responses and responses[0].status == 200, (
            f"Ожидали 200, получили {responses[0].status if responses else 'нет ответа'}"
        )

    def test_save_shows_success_feedback(
        self, terminal_edit_with_restore, page: Page
    ):
        """После успешного сохранения появляется уведомление об успехе."""
        edit_page, _, _ = terminal_edit_with_restore
        edit_page.save_btn.click()
        page.wait_for_load_state("networkidle")
        feedback = (
            page.locator("[role=alert]")
            .or_(page.locator(".notification, .toast, .snackbar"))
            .or_(page.get_by_text("успешно", exact=False))
        )
        expect(feedback.first).to_be_visible(timeout=5000)

    def test_save_persists_public_name(
        self, terminal_edit_with_restore, page: Page
    ):
        """После сохранения поле public_name отображает новое значение."""
        edit_page, service_id, client = terminal_edit_with_restore
        new_name = "QA Saved Name"
        edit_page.public_name_input.fill(new_name)
        edit_page.save_btn.click()
        page.wait_for_load_state("networkidle")
        saved = client.get_terminal(service_id).json()["response"]["public_name"]
        assert saved == new_name, (
            f"На бэке сохранилось {saved!r}, ожидалось {new_name!r}"
        )
