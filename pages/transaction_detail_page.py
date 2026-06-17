from playwright.sync_api import Page
from pages.base_page import BasePage


class TransactionDetailPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Three <a href='/new/transactions'> exist (sidebar, breadcrumb, back button)
        # Target only the back button (MuiButton-root)
        self.back_link = page.locator("a[href='/new/transactions'][class*='MuiButton-root']")
        self.title = page.locator("h1")
        self.refund_btn = page.get_by_role("button", name="Возврат")
        self.send_webhook_btn = page.get_by_role("button", name="Отправить вебхук")
        self.section_history = page.locator("h2").filter(has_text="История статусов")
        self.section_payment_details = page.locator("h2").filter(has_text="Детали платежа")
        self.section_payment_data = page.locator("h2").filter(has_text="Платежные данные")

        # Breadcrumbs — MUI renders <nav class="...MuiBreadcrumbs-root..."> without aria-label
        self.breadcrumbs_nav = page.locator("nav[class*='MuiBreadcrumbs-root']")
        self.breadcrumb_transactions_link = page.locator("nav[class*='MuiBreadcrumbs-root'] a[href='/new/transactions']")
        # Current page is a <p> element (last breadcrumb item, no aria-current set by MUI)
        self.breadcrumb_detail_current = page.locator("nav[class*='MuiBreadcrumbs-root'] p")

        # Page header: h4 shows "{cost} {currency}", div shows status text
        self.header_amount = page.locator("h4[class*='MuiTypography-h4']")
        self.header_status = page.locator("h4[class*='MuiTypography-h4'] ~ div")

        # History timeline — dates rendered as MuiTypography-caption, status/amount as <p>
        self.history_timeline_dates = page.locator("span[class*='MuiTypography-caption']")
        self.history_timeline_statuses = page.locator(
            "h2:has-text('История статусов') ~ * p[class*='MuiTypography-body1']"
        )

        # Payment Details card — field labels
        self.detail_order_id_label = page.get_by_text("ID заказа")
        self.detail_tran_id_label = page.get_by_text("ID транзакции")
        self.detail_fee_label = page.get_by_text("Сумма комиссии")
        self.detail_payment_method_label = page.get_by_text("Метод оплаты")
        self.detail_mode_label = page.get_by_text("Режим")

        # Copy icon buttons (beside order_id and tran_id in payment details)
        # MUI renders icon buttons without data-testid; target MuiIconButton-root
        self.copy_buttons = page.locator("[class*='MuiIconButton-root']")

        # Payment Data card — field labels
        self.data_masked_pan_label = page.get_by_text("Номер карты")
        self.data_cardholder_label = page.get_by_text("Держатель карты")
        self.data_email_label = page.get_by_text("Email")
        self.data_phone_label = page.get_by_text("Номер телефона")
        self.data_p2p_requisite_label = page.get_by_text("P2P Реквизит")

        # Toast/snackbar notification
        self.notification = page.locator("[role='alert']")

    def is_loaded(self) -> bool:
        return "/new/transactions/" in self.page.url

    def go_back(self):
        self.back_link.click()
        self.page.wait_for_load_state("networkidle")
