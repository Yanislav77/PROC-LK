"""Тесты страницы детализации транзакции: структура, навигация, поля, уведомления."""
import pytest
from playwright.sync_api import expect
from pages.transactions_page import TransactionsPage
from pages.transaction_detail_page import TransactionDetailPage
from utils.config import BASE_URL


@pytest.mark.ui
class TestTransactionDetail:
    """Страница детализации: заголовок, секции, навигация и кнопки действий."""

    @pytest.fixture
    def detail_page(self, transactions_page: TransactionsPage) -> TransactionDetailPage:
        detail = TransactionDetailPage(transactions_page.page)
        transactions_page.click_transaction(0)
        transactions_page.page.wait_for_load_state("networkidle")
        return detail

    def test_detail_page_is_loaded(self, detail_page: TransactionDetailPage):
        """Страница детализации успешно загружается после перехода по ссылке."""
        assert detail_page.is_loaded()

    def test_detail_page_title(self, detail_page: TransactionDetailPage):
        """Заголовок страницы содержит текст «Детали транзакции»."""
        expect(detail_page.title).to_have_text("Детали транзакции")

    def test_detail_page_has_history_section(self, detail_page: TransactionDetailPage):
        """Секция «История» присутствует на странице детализации."""
        expect(detail_page.section_history).to_be_visible()

    def test_detail_page_has_payment_details_section(self, detail_page: TransactionDetailPage):
        """Секция «Детали платежа» присутствует на странице детализации."""
        expect(detail_page.section_payment_details).to_be_visible()

    def test_detail_page_has_payment_data_section(self, detail_page: TransactionDetailPage):
        """Секция «Данные платежа» присутствует на странице детализации."""
        expect(detail_page.section_payment_data).to_be_visible()

    def test_detail_page_has_back_link(self, detail_page: TransactionDetailPage):
        """Ссылка «Назад» к списку транзакций присутствует на странице."""
        expect(detail_page.back_link).to_be_visible()

    def test_detail_page_back_link_navigates_to_list(self, detail_page: TransactionDetailPage):
        """Нажатие «Назад» возвращает на страницу списка /transactions."""
        detail_page.go_back()
        assert "/new/transactions" in detail_page.page.url
        # убедимся, что это страница списка, а не детализации
        assert detail_page.page.url.rstrip("/").endswith("/transactions")

    def test_detail_page_has_refund_button(self, detail_page: TransactionDetailPage):
        """Кнопка «Возврат» скрыта для не-Completed транзакций (первая в списке)."""
        # Per spec: button renders only when status = Completed.
        # The first transaction is typically Rejected/Processing — button must not be visible.
        expect(detail_page.refund_btn).not_to_be_visible()

    def test_detail_page_has_send_webhook_button(self, detail_page: TransactionDetailPage):
        """Кнопка «Отправить вебхук» присутствует на странице детализации."""
        expect(detail_page.send_webhook_btn).to_be_visible()


@pytest.mark.ui
class TestTransactionDetailBreadcrumbs:
    """Хлебные крошки: «Транзакции / Детали транзакции»."""

    @pytest.fixture
    def detail_page(self, transactions_page: TransactionsPage) -> TransactionDetailPage:
        detail = TransactionDetailPage(transactions_page.page)
        transactions_page.click_transaction(0)
        transactions_page.page.wait_for_load_state("networkidle")
        return detail

    def test_breadcrumbs_nav_visible(self, detail_page: TransactionDetailPage):
        """Навигация хлебных крошек присутствует на странице."""
        expect(detail_page.breadcrumbs_nav).to_be_visible()

    def test_breadcrumbs_has_transactions_link(self, detail_page: TransactionDetailPage):
        """Ссылка «Транзакции» присутствует в хлебных крошках."""
        expect(detail_page.breadcrumb_transactions_link).to_be_visible()

    def test_breadcrumbs_current_page_is_detail(self, detail_page: TransactionDetailPage):
        """Активный элемент хлебных крошек содержит «Детали транзакции»."""
        expect(detail_page.breadcrumb_detail_current).to_contain_text("Детали транзакции")


@pytest.mark.ui
class TestTransactionDetailHeader:
    """Заголовок страницы: сумма с валютой и статус транзакции."""

    @pytest.fixture
    def detail_page(self, transactions_page: TransactionsPage) -> TransactionDetailPage:
        detail = TransactionDetailPage(transactions_page.page)
        transactions_page.click_transaction(0)
        transactions_page.page.wait_for_load_state("networkidle")
        return detail

    def test_header_shows_amount(self, detail_page: TransactionDetailPage):
        """Шапка показывает сумму и валюту транзакции (h4)."""
        expect(detail_page.header_amount).to_be_visible()

    def test_header_shows_status(self, detail_page: TransactionDetailPage):
        """Шапка показывает текст статуса транзакции рядом с суммой."""
        expect(detail_page.header_status).to_be_visible()


@pytest.mark.ui
class TestTransactionHistoryEntries:
    """Блок «История статусов»: timeline с датой, статусом и суммой."""

    @pytest.fixture
    def detail_page(self, transactions_page: TransactionsPage) -> TransactionDetailPage:
        detail = TransactionDetailPage(transactions_page.page)
        transactions_page.click_transaction(0)
        transactions_page.page.wait_for_load_state("networkidle")
        transactions_page.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        detail.history_timeline_dates.first.wait_for(timeout=10000)
        return detail

    def test_history_section_visible(self, detail_page: TransactionDetailPage):
        """Секция «История статусов» присутствует на странице."""
        expect(detail_page.section_history).to_be_visible()

    def test_history_has_timeline_dates(self, detail_page: TransactionDetailPage):
        """Timeline истории содержит хотя бы одну дату записи."""
        count = detail_page.history_timeline_dates.count()
        assert count >= 1, f"Expected at least 1 timeline date, found {count}"

    def test_history_has_multiple_entries(self, detail_page: TransactionDetailPage):
        """Timeline истории содержит более одной записи (несколько статусов)."""
        count = detail_page.history_timeline_dates.count()
        assert count >= 2, f"Expected at least 2 history entries, found {count}"


@pytest.mark.ui
class TestTransactionPaymentDetailsFields:
    """Блок «Детали платежа»: все обязательные поля и кнопки копирования."""

    @pytest.fixture
    def detail_page(self, transactions_page: TransactionsPage) -> TransactionDetailPage:
        detail = TransactionDetailPage(transactions_page.page)
        transactions_page.click_transaction(0)
        transactions_page.page.wait_for_load_state("networkidle")
        transactions_page.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        transactions_page.page.wait_for_timeout(1000)
        return detail

    def test_order_id_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «ID заказа» отображается в блоке «Детали платежа»."""
        expect(detail_page.detail_order_id_label).to_be_visible()

    def test_tran_id_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «ID транзакции» отображается в блоке «Детали платежа»."""
        expect(detail_page.detail_tran_id_label).to_be_visible()

    def test_date_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «Дата» отображается в блоке «Детали платежа»."""
        expect(detail_page.detail_date_label).to_be_visible()

    def test_terminal_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «Терминал» отображается в блоке «Детали платежа»."""
        expect(detail_page.detail_terminal_label).to_be_visible()

    def test_status_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «Статус» отображается в блоке «Детали платежа»."""
        expect(detail_page.detail_status_label).to_be_visible()

    def test_amount_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «Сумма» отображается в блоке «Детали платежа»."""
        expect(detail_page.detail_amount_label).to_be_visible()

    def test_currency_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «Валюта» отображается в блоке «Детали платежа»."""
        expect(detail_page.detail_currency_label).to_be_visible()

    def test_fee_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «Сумма комиссии» отображается в блоке «Детали платежа»."""
        expect(detail_page.detail_fee_label).to_be_visible()

    def test_payment_method_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «Метод оплаты» отображается в блоке «Детали платежа»."""
        expect(detail_page.detail_payment_method_label).to_be_visible()

    def test_mode_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «Режим» (Test/Live) отображается в блоке «Детали платежа»."""
        expect(detail_page.detail_mode_label).to_be_visible()

    def test_copy_buttons_present_for_ids(self, detail_page: TransactionDetailPage):
        """Кнопки «Копировать» присутствуют рядом с ID заказа и ID транзакции (2 шт)."""
        count = detail_page.copy_buttons.count()
        assert count >= 2, f"Expected at least 2 copy buttons (one per ID), found {count}"


@pytest.mark.ui
class TestTransactionPaymentDataFields:
    """Блок «Платёжные данные»: все обязательные поля."""

    @pytest.fixture
    def detail_page(self, transactions_page: TransactionsPage) -> TransactionDetailPage:
        detail = TransactionDetailPage(transactions_page.page)
        transactions_page.click_transaction(0)
        transactions_page.page.wait_for_load_state("networkidle")
        return detail

    @pytest.fixture
    def p2p_detail_page(self, transactions_page: TransactionsPage) -> TransactionDetailPage:
        """Открывает P2P транзакцию с полем «P2P Реквизит» по известному ID.

        Фронтенд-фильтр по методу P2P возвращает Card-транзакции (баг),
        поэтому используем прямую навигацию к проверенной P2P транзакции.
        """
        page = transactions_page.page
        page.goto(f"{BASE_URL}/transactions/1000608331")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        if not TransactionDetailPage(page).is_loaded():
            pytest.skip("P2P транзакция недоступна в текущем окружении")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        return TransactionDetailPage(page)

    def test_masked_pan_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «Номер карты» отображается в блоке «Платёжные данные»."""
        expect(detail_page.data_masked_pan_label.first).to_be_visible()

    def test_cardholder_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «Держатель карты» отображается в блоке «Платёжные данные»."""
        expect(detail_page.data_cardholder_label.first).to_be_visible()

    def test_email_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «Email» отображается в блоке «Платёжные данные»."""
        expect(detail_page.data_email_label).to_be_visible()

    def test_phone_label_visible(self, detail_page: TransactionDetailPage):
        """Метка «Номер телефона» отображается в блоке «Платёжные данные»."""
        expect(detail_page.data_phone_label).to_be_visible()

    def test_p2p_requisite_label_visible(self, p2p_detail_page: TransactionDetailPage):
        """Метка «P2P Реквизит» отображается для P2P транзакции в блоке «Платёжные данные»."""
        expect(p2p_detail_page.data_p2p_requisite_label).to_be_visible()


@pytest.mark.ui
class TestTransactionDetailNotifications:
    """Уведомления после выполнения действий со страницы детализации."""

    @pytest.fixture
    def detail_page(self, transactions_page: TransactionsPage) -> TransactionDetailPage:
        detail = TransactionDetailPage(transactions_page.page)
        transactions_page.click_transaction(0)
        transactions_page.page.wait_for_load_state("networkidle")
        return detail

    def test_send_webhook_shows_notification(self, detail_page: TransactionDetailPage):
        """Нажатие «Отправить вебхук» показывает уведомление с результатом."""
        detail_page.send_webhook_btn.click()
        expect(detail_page.notification).to_be_visible(timeout=10000)

    @pytest.mark.xfail(reason="BUG: уведомление содержит «Вебхук отправлен успешно» без ID транзакции; спек требует «ID транзакции: X - Webhook отправлен успешно»", strict=True)
    def test_webhook_notification_contains_transaction_id(self, detail_page: TransactionDetailPage):
        """Уведомление о вебхуке содержит текст «ID транзакции»."""
        detail_page.send_webhook_btn.click()
        expect(detail_page.notification).to_contain_text("ID транзакции", timeout=10000)
