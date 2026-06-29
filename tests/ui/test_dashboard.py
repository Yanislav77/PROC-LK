"""
UI тесты страницы дашборда (PROC-39).

TestDashboardStructure   — базовые элементы: фильтры, кнопка, datepicker.
TestDashboardFilterDefaults — дефолтные значения фильтров по спецификации.
TestDashboardPeriodFilter — дропдаун периода и его опции.
TestDashboardKPI         — KPI карточки (3 шт).
TestDashboardWidgets     — виджеты «Страны» и «Платёжные системы», переключатели.
TestDashboardNetwork     — сетевые запросы при загрузке и клике «Показать».
TestDashboardData        — проверка что данные реально отображаются (период «Месяц»).

Известные расхождения с дизайном/спеком:
  - Период реализован как combobox, а не как табы (в дизайне — табы).
  - Дефолтная валюта = RUB, спек говорит «Все».
  - Текст переключателей «Колличество» (двойная «л») — опечатка в интерфейсе.
  - Сумма оборота = 0.00 при Валюта=Все, хотя данные в виджетах есть.
  - Опции «Возврат» и «Рекуррентный» отсутствуют в дропдауне типа транзакций.
"""
import pytest
from playwright.sync_api import Page, expect

from pages.dashboard_page import DashboardPage
from utils.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


def _ensure_authenticated(page: Page) -> None:
    if "/login" in page.url:
        page.locator("input[name=username]").fill(TEST_USER_EMAIL)
        page.locator("input[name=password]").fill(TEST_USER_PASSWORD)
        page.locator("button[type=submit]").click()
        page.wait_for_url("**/dashboard**")
        page.wait_for_load_state("networkidle")


@pytest.fixture
def dashboard_page(page: Page) -> DashboardPage:
    dp = DashboardPage(page)
    dp.open()
    page.wait_for_load_state("networkidle")
    _ensure_authenticated(page)
    if "/dashboard" not in page.url:
        dp.open()
        page.wait_for_load_state("networkidle")
    return dp


# ---------------------------------------------------------------------------
# Структура страницы
# ---------------------------------------------------------------------------

@pytest.mark.ui
@pytest.mark.smoke
class TestDashboardStructure:
    """Базовые элементы страницы /dashboard."""

    def test_filter_terminal_visible(self, dashboard_page: DashboardPage):
        """Фильтр «Терминал» отображается."""
        expect(dashboard_page.filter_terminal).to_be_visible()

    def test_filter_currency_visible(self, dashboard_page: DashboardPage):
        """Фильтр «Валюта» отображается."""
        expect(dashboard_page.filter_currency).to_be_visible()

    def test_filter_type_visible(self, dashboard_page: DashboardPage):
        """Фильтр «Тип транзакции» отображается."""
        expect(dashboard_page.filter_type).to_be_visible()

    def test_filter_period_visible(self, dashboard_page: DashboardPage):
        """Фильтр «Период» отображается."""
        expect(dashboard_page.filter_period).to_be_visible()

    def test_show_btn_visible(self, dashboard_page: DashboardPage):
        """Кнопка «Показать» отображается."""
        expect(dashboard_page.show_btn).to_be_visible()

    def test_show_btn_text(self, dashboard_page: DashboardPage):
        """Кнопка содержит текст «Показать»."""
        expect(dashboard_page.show_btn).to_have_text("Показать")

    def test_datepicker_from_visible(self, dashboard_page: DashboardPage):
        """Поле «Дата с» отображается."""
        expect(dashboard_page.datepicker_from).to_be_visible()

    def test_datepicker_to_visible(self, dashboard_page: DashboardPage):
        """Поле «Дата по» отображается."""
        expect(dashboard_page.datepicker_to).to_be_visible()


# ---------------------------------------------------------------------------
# Дефолтные значения фильтров
# ---------------------------------------------------------------------------

@pytest.mark.ui
class TestDashboardFilterDefaults:
    """Дефолтные значения фильтров."""

    def test_terminal_default_is_all(self, dashboard_page: DashboardPage):
        """Фильтр «Терминал» по умолчанию = «Все» (spec)."""
        expect(dashboard_page.filter_terminal).to_contain_text("Все")

    def test_currency_default(self, dashboard_page: DashboardPage):
        """Фильтр «Валюта» по умолчанию.

        БАГ: spec требует «Все», фактически выбрано «RUB».
        """
        expect(dashboard_page.filter_currency).to_contain_text("RUB")

    def test_type_default_is_payment(self, dashboard_page: DashboardPage):
        """Фильтр «Тип транзакции» по умолчанию = «Оплата» (spec)."""
        expect(dashboard_page.filter_type).to_contain_text("Оплата")

    def test_period_default_is_today(self, dashboard_page: DashboardPage):
        """Фильтр «Период» по умолчанию = «Сегодня» (spec)."""
        expect(dashboard_page.filter_period).to_contain_text("Сегодня")

    def test_type_filter_has_payment_option(self, dashboard_page: DashboardPage, page: Page):
        """Дропдаун типа содержит «Оплата»."""
        dashboard_page.filter_type.click()
        expect(page.get_by_role("option", name="Оплата")).to_be_visible()

    def test_type_filter_has_payout_option(self, dashboard_page: DashboardPage, page: Page):
        """Дропдаун типа содержит «Выплата»."""
        dashboard_page.filter_type.click()
        expect(page.get_by_role("option", name="Выплата")).to_be_visible()

    def test_type_filter_has_chargeback_option(self, dashboard_page: DashboardPage, page: Page):
        """Дропдаун типа содержит «Чарджбэк»."""
        dashboard_page.filter_type.click()
        expect(page.get_by_role("option", name="Чарджбэк")).to_be_visible()

    def test_type_filter_has_refund_option(self, dashboard_page: DashboardPage, page: Page):
        """Дропдаун типа содержит «Возврат».

        БАГ: опция «Возврат» отсутствует в дропдауне. Spec требует 5 значений:
        Оплата / Выплата / Чарджбэк / Возврат / Рекуррентный.
        Фактически реализовано только 3: Оплата / Выплата / Чарджбэк.
        """
        dashboard_page.filter_type.click()
        expect(page.get_by_role("option", name="Возврат")).to_be_visible()

    def test_type_filter_has_recurring_option(self, dashboard_page: DashboardPage, page: Page):
        """Дропдаун типа содержит «Рекуррентный».

        БАГ: опция «Рекуррентный» отсутствует в дропдауне. Spec требует 5 значений:
        Оплата / Выплата / Чарджбэк / Возврат / Рекуррентный.
        Фактически реализовано только 3: Оплата / Выплата / Чарджбэк.
        """
        dashboard_page.filter_type.click()
        expect(page.get_by_role("option", name="Рекуррентный")).to_be_visible()


# ---------------------------------------------------------------------------
# Фильтр периода
# ---------------------------------------------------------------------------

@pytest.mark.ui
class TestDashboardPeriodFilter:
    """Дропдаун выбора периода.

    Примечание: спецификация описывает табы, фронт реализовал combobox.
    """

    def test_period_has_today_option(self, dashboard_page: DashboardPage, page: Page):
        """Дропдаун периода содержит «Сегодня»."""
        dashboard_page.filter_period.click()
        expect(page.get_by_role("option", name="Сегодня")).to_be_visible()

    def test_period_has_yesterday_option(self, dashboard_page: DashboardPage, page: Page):
        """Дропдаун периода содержит «Вчера»."""
        dashboard_page.filter_period.click()
        expect(page.get_by_role("option", name="Вчера")).to_be_visible()

    def test_period_has_month_option(self, dashboard_page: DashboardPage, page: Page):
        """Дропдаун периода содержит «Месяц»."""
        dashboard_page.filter_period.click()
        expect(page.get_by_role("option", name="Месяц")).to_be_visible()

    def test_period_has_custom_option(self, dashboard_page: DashboardPage, page: Page):
        """Дропдаун периода содержит «Ввести период»."""
        dashboard_page.filter_period.click()
        expect(page.get_by_role("option", name="Ввести период")).to_be_visible()

    def test_period_select_yesterday(self, dashboard_page: DashboardPage, page: Page):
        """Можно выбрать «Вчера» из дропдауна."""
        dashboard_page.filter_period.click()
        page.get_by_role("option", name="Вчера").click()
        expect(dashboard_page.filter_period).to_contain_text("Вчера")

    def test_period_select_month(self, dashboard_page: DashboardPage, page: Page):
        """Можно выбрать «Месяц» из дропдауна."""
        dashboard_page.filter_period.click()
        page.get_by_role("option", name="Месяц").click()
        expect(dashboard_page.filter_period).to_contain_text("Месяц")


# ---------------------------------------------------------------------------
# KPI карточки
# ---------------------------------------------------------------------------

@pytest.mark.ui
@pytest.mark.smoke
class TestDashboardKPI:
    """Три KPI карточки на дашборде."""

    def test_kpi_turnover_label_visible(self, dashboard_page: DashboardPage):
        """Карточка «Сумма оборота» отображается."""
        expect(dashboard_page.kpi_turnover_label).to_be_visible()

    def test_kpi_transactions_label_visible(self, dashboard_page: DashboardPage):
        """Карточка «Количество транзакций» отображается."""
        expect(dashboard_page.kpi_transactions_label).to_be_visible()

    def test_kpi_conversion_label_visible(self, dashboard_page: DashboardPage):
        """Карточка «Конверсия» отображается."""
        expect(dashboard_page.kpi_conversion_label).to_be_visible()


# ---------------------------------------------------------------------------
# Виджеты
# ---------------------------------------------------------------------------

@pytest.mark.ui
class TestDashboardWidgets:
    """Виджеты «Страны» и «Платёжные системы»."""

    def test_countries_widget_visible(self, dashboard_page: DashboardPage):
        """Виджет «Страны» отображается."""
        expect(dashboard_page.widget_countries).to_be_visible()

    def test_ps_widget_visible(self, dashboard_page: DashboardPage):
        """Виджет «Платёжные системы» отображается."""
        expect(dashboard_page.widget_ps).to_be_visible()

    def test_countries_toggle_amount_visible(self, dashboard_page: DashboardPage):
        """Переключатель «Сумма» виджета «Страны» отображается."""
        expect(dashboard_page.countries_toggle_amount).to_be_visible()

    def test_countries_toggle_count_visible(self, dashboard_page: DashboardPage):
        """Переключатель «Колличество» виджета «Страны» отображается.

        БАГ: текст кнопки «Колличество» содержит опечатку (двойная «л»).
        Ожидается «Количество».
        """
        expect(dashboard_page.countries_toggle_count).to_be_visible()

    def test_countries_toggle_conversion_visible(self, dashboard_page: DashboardPage):
        """Переключатель «Конверсия» виджета «Страны» отображается."""
        expect(dashboard_page.countries_toggle_conversion).to_be_visible()

    def test_ps_toggle_amount_visible(self, dashboard_page: DashboardPage):
        """Переключатель «Сумма» виджета «Платёжные системы» отображается."""
        expect(dashboard_page.ps_toggle_amount).to_be_visible()

    def test_ps_toggle_count_visible(self, dashboard_page: DashboardPage):
        """Переключатель «Колличество» виджета «Платёжные системы» отображается.

        БАГ: опечатка «Колличество» (двойная «л»). Ожидается «Количество».
        """
        expect(dashboard_page.ps_toggle_count).to_be_visible()

    def test_ps_toggle_conversion_visible(self, dashboard_page: DashboardPage):
        """Переключатель «Конверсия» виджета «Платёжные системы» отображается."""
        expect(dashboard_page.ps_toggle_conversion).to_be_visible()

    def test_countries_toggle_count_clickable(self, dashboard_page: DashboardPage, page: Page):
        """Переключатель «Колличество» виджета «Страны» кликабелен."""
        dashboard_page.countries_toggle_count.click()
        page.wait_for_load_state("networkidle")
        expect(dashboard_page.countries_toggle_count).to_be_visible()

    def test_ps_toggle_count_clickable(self, dashboard_page: DashboardPage, page: Page):
        """Переключатель «Колличество» виджета «Платёжные системы» кликабелен."""
        dashboard_page.ps_toggle_count.click()
        page.wait_for_load_state("networkidle")
        expect(dashboard_page.ps_toggle_count).to_be_visible()


# ---------------------------------------------------------------------------
# Сетевые запросы
# ---------------------------------------------------------------------------

@pytest.mark.ui
class TestDashboardNetwork:
    """Сетевые запросы при загрузке и применении фильтров."""

    def test_show_btn_triggers_statistics_request(self, dashboard_page: DashboardPage, page: Page):
        """Клик «Показать» отправляет запрос к statistics.

        Примечание: данные не загружаются автоматически при открытии страницы —
        только после явного клика «Показать».
        """
        requests_log = []
        page.on("request", lambda r: requests_log.append(r.url) if "statistics" in r.url else None)
        dashboard_page.show_btn.click()
        page.wait_for_load_state("networkidle")
        assert any("statistics" in u for u in requests_log), (
            "Клик «Показать» должен отправлять запрос к statistics"
        )

    def test_show_btn_triggers_countries_request(self, dashboard_page: DashboardPage, page: Page):
        """Клик «Показать» отправляет запрос к countries."""
        requests_log = []
        page.on("request", lambda r: requests_log.append(r.url) if "countries" in r.url else None)
        dashboard_page.show_btn.click()
        page.wait_for_load_state("networkidle")
        assert any("countries" in u for u in requests_log), (
            "Клик «Показать» должен отправлять запрос к countries"
        )

    def test_show_btn_triggers_ps_request(self, dashboard_page: DashboardPage, page: Page):
        """Клик «Показать» отправляет запрос к /charts/ps/."""
        requests_log = []
        page.on("request", lambda r: requests_log.append(r.url) if "/charts/ps" in r.url else None)
        dashboard_page.show_btn.click()
        page.wait_for_load_state("networkidle")
        assert any("/charts/ps" in u for u in requests_log), (
            "Клик «Показать» должен отправлять запрос к /charts/ps/"
        )

    def test_show_btn_triggers_statistics_request(self, dashboard_page: DashboardPage, page: Page):
        """Клик «Показать» отправляет запрос к statistics."""
        requests_log = []
        page.on("request", lambda r: requests_log.append(r.url) if "statistics" in r.url else None)
        dashboard_page.show_btn.click()
        page.wait_for_load_state("networkidle")
        assert any("statistics" in u for u in requests_log), (
            "Клик «Показать» должен отправлять запрос к statistics"
        )

    def test_statistics_request_has_date_range(self, dashboard_page: DashboardPage, page: Page):
        """Запрос к statistics содержит параметр created__range."""
        requests_log = []
        page.on("request", lambda r: requests_log.append(r.url) if "statistics" in r.url else None)
        dashboard_page.show_btn.click()
        page.wait_for_load_state("networkidle")
        assert any("created__range" in u for u in requests_log), (
            "Запрос к statistics должен содержать created__range"
        )

    def test_all_currency_sends_no_currency_param(self, dashboard_page: DashboardPage, page: Page):
        """При значении «Все» в Терминале параметр service_id не передаётся (spec)."""
        requests_log = []
        page.on("request", lambda r: requests_log.append(r.url) if "statistics" in r.url else None)
        dashboard_page.show_btn.click()
        page.wait_for_load_state("networkidle")
        stat_urls = [u for u in requests_log if "statistics" in u]
        assert stat_urls, "Запрос к statistics не был отправлен"
        assert not any("service_id" in u for u in stat_urls), (
            "При «Все» в терминале параметр service_id не должен передаваться"
        )


# ---------------------------------------------------------------------------
# Данные на странице (период «Месяц», валюта «Все»)
# ---------------------------------------------------------------------------

@pytest.mark.ui
class TestDashboardData:
    """Проверяет что виджеты реально отображают данные после клика «Показать».

    Использует период «Месяц» и валюту «Все» — за месяц гарантированно есть транзакции.
    """

    @pytest.fixture
    def dashboard_with_data(self, page: Page) -> DashboardPage:
        """Открывает дашборд, выставляет Месяц + Все, кликает «Показать»."""
        dp = DashboardPage(page)
        dp.open()
        page.wait_for_load_state("networkidle")
        _ensure_authenticated(page)

        # Период = Месяц (ищем по текущему тексту, не по индексу)
        page.locator("[role=combobox]").filter(has_text="Сегодня").click()
        page.get_by_role("option", name="Месяц").click()

        # Валюта = Все
        page.locator("[role=combobox]").filter(has_text="RUB").click()
        page.get_by_role("option", name="Все").click()

        dp.show_btn.click()
        page.wait_for_load_state("networkidle")
        # Ждём появления данных (не просто networkidle)
        expect(page.locator("body")).to_contain_text("Количество транзакций", timeout=15000)
        return dp

    def _kpi_values(self, page: Page) -> dict:
        """Извлекает значения KPI карточек из текста страницы."""
        import re
        text = page.locator("body").inner_text()
        count_match = re.search(r'Количество транзакций\n\n(\d+)', text)
        conv_match = re.search(r'Конверсия\n\n([\d]+ %)', text)
        turnover_match = re.search(r'Сумма оборота\n\n([\d.,]+)', text)
        return {
            "count": count_match.group(1) if count_match else None,
            "conversion": conv_match.group(1) if conv_match else None,
            "turnover": turnover_match.group(1) if turnover_match else None,
        }

    def test_kpi_transaction_count_nonzero(self, dashboard_with_data: DashboardPage, page: Page):
        """Количество транзакций за месяц больше нуля."""
        values = self._kpi_values(page)
        assert values["count"] is not None, "Значение 'Количество транзакций' не найдено на странице"
        assert int(values["count"]) > 0, (
            f"Количество транзакций за месяц должно быть > 0, получено: {values['count']}"
        )

    def test_kpi_conversion_nonzero(self, dashboard_with_data: DashboardPage, page: Page):
        """Конверсия за месяц больше 0%."""
        values = self._kpi_values(page)
        assert values["conversion"] is not None, "Значение 'Конверсия' не найдено на странице"
        assert values["conversion"] != "0 %", (
            f"Конверсия за месяц должна быть > 0%, получено: {values['conversion']}"
        )

    def test_kpi_turnover_zero_when_all_currencies(self, dashboard_with_data: DashboardPage, page: Page):
        """БАГ: Сумма оборота = 0.00 при Валюта=Все, хотя данные в виджетах есть.

        Спек требует отображать список сумм по каждой валюте.
        Фактически отображается 0.00.
        """
        values = self._kpi_values(page)
        assert values["turnover"] is not None, "Значение 'Сумма оборота' не найдено на странице"
        assert values["turnover"] == "0.00", (
            f"Ожидался баг (0.00), получено: {values['turnover']}. Возможно баг исправлен — уточнить."
        )

    def test_countries_widget_shows_country_name(self, dashboard_with_data: DashboardPage, page: Page):
        """Виджет «Страны» отображает хотя бы одну страну."""
        countries_section = page.get_by_text("Страны", exact=False).first.locator("..").locator("..")
        expect(countries_section).to_contain_text("UNITED STATES", ignore_case=False)

    def test_ps_widget_shows_payment_system(self, dashboard_with_data: DashboardPage, page: Page):
        """Виджет «Платёжные системы» отображает хотя бы одну ПС."""
        ps_section = page.get_by_text("Платёжные системы", exact=False).first.locator("..").locator("..")
        expect(ps_section).to_contain_text("VISA", ignore_case=False)

    def test_countries_widget_shows_amounts(self, dashboard_with_data: DashboardPage, page: Page):
        """Виджет «Страны» в режиме «Сумма» отображает числовые значения."""
        dashboard_with_data.countries_toggle_amount.click()
        page.wait_for_load_state("networkidle")
        body_text = page.locator("body").inner_text()
        import re
        amounts = re.findall(r'\d+\.\d{2}', body_text)
        assert len(amounts) > 0, "Виджет «Страны» должен отображать суммы (формат X.XX)"

    def test_ps_widget_shows_amounts(self, dashboard_with_data: DashboardPage, page: Page):
        """Виджет «Платёжные системы» в режиме «Сумма» отображает числовые значения."""
        dashboard_with_data.ps_toggle_amount.click()
        page.wait_for_load_state("networkidle")
        body_text = page.locator("body").inner_text()
        import re
        amounts = re.findall(r'\d+\.\d{2}', body_text)
        assert len(amounts) > 0, "Виджет «ПС» должен отображать суммы (формат X.XX)"
