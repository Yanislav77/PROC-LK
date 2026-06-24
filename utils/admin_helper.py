import threading
import uuid
from playwright.sync_api import sync_playwright

from utils.config import ADMIN_URL, ADMIN_USER, ADMIN_PASSWORD


def _do_admin_login(page, admin_url, admin_user, admin_password):
    page.goto(f"{admin_url}/login/?next={admin_url}/")
    page.locator("input[name=username]").fill(admin_user)
    page.locator("input[name=password]").fill(admin_password)
    page.locator("input[type=submit], button[type=submit]").first.click()
    page.wait_for_load_state("networkidle")


def _remove_debug_toolbar(page):
    page.evaluate("var el = document.getElementById('djDebug'); if(el) el.remove();")


def create_fresh_tfa_user() -> tuple[str, str, int]:
    """Создаёт тестового пользователя в админке с настройками для прохождения TFA setup.

    Выставляет: Тема Spirita = proc_v1, is_partner, is_staff, is_superuser.
    Возвращает (username, password, user_id).
    Запускается в отдельном потоке — вне asyncio-цикла pytest-playwright.
    """
    username = f"test_tfa_{uuid.uuid4().hex[:8]}"
    password = "TestPass123!"
    result = []

    def _run():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            _do_admin_login(page, ADMIN_URL, ADMIN_USER, ADMIN_PASSWORD)

            # Шаг 1: создать пользователя
            page.goto(f"{ADMIN_URL}/core/user/add/")
            page.wait_for_load_state("networkidle")
            page.locator("input[name=username]").fill(username)
            page.locator("input[name=password]").fill(password)
            _remove_debug_toolbar(page)
            page.locator("input[name=_save]").click()
            page.wait_for_load_state("networkidle")

            # URL после сохранения: /admin/core/user/{id}/change/
            user_id = int(page.url.rstrip("/").split("/")[-2])

            # Шаг 2: выставить обязательные поля на странице редактирования
            _remove_debug_toolbar(page)
            page.select_option("select[name=spirit_theme]", "12")  # proc_v1
            page.locator("input[name=is_partner]").check()
            page.locator("input[name=is_staff]").check()
            page.locator("input[name=is_superuser]").check()
            page.locator("input[name=_save]").click()
            page.wait_for_load_state("networkidle")

            browser.close()
            result.append((username, password, user_id))

    t = threading.Thread(target=_run)
    t.start()
    t.join()
    return result[0]


def get_user_id_by_username(username: str) -> int:
    """Находит ID пользователя по username через поиск в админке."""
    result = []

    def _run():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            _do_admin_login(page, ADMIN_URL, ADMIN_USER, ADMIN_PASSWORD)
            page.goto(f"{ADMIN_URL}/core/user/?q={username}")
            page.wait_for_load_state("networkidle")
            link = page.locator("table#result_list tbody tr td a").first
            href = link.get_attribute("href")
            user_id = int(href.rstrip("/").split("/")[-2])
            browser.close()
            result.append(user_id)

    t = threading.Thread(target=_run)
    t.start()
    t.join()
    return result[0]


def _set_checkbox(user_id: int, field_name: str, value: bool) -> None:
    """Устанавливает/снимает чекбокс у пользователя в админке."""
    def _run():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            _do_admin_login(page, ADMIN_URL, ADMIN_USER, ADMIN_PASSWORD)
            page.goto(f"{ADMIN_URL}/core/user/{user_id}/change/")
            page.wait_for_load_state("networkidle")
            _remove_debug_toolbar(page)
            cb = page.locator(f"input[name={field_name}]")
            if value:
                cb.check()
            else:
                cb.uncheck()
            page.locator("input[name=_save]").click()
            page.wait_for_load_state("networkidle")
            browser.close()

    t = threading.Thread(target=_run)
    t.start()
    t.join()


def set_ignore_tfa(user_id: int, ignore: bool) -> None:
    """Устанавливает или снимает флаг 'Игнорировать TFA' для пользователя в админке."""
    _set_checkbox(user_id, "ignore_tfa", ignore)


def set_use_tfa(user_id: int, value: bool) -> None:
    """Включает или выключает TFA для пользователя напрямую через админку."""
    _set_checkbox(user_id, "use_tfa", value)


def create_tfa_enabled_user() -> tuple[str, str, str, int]:
    """Создаёт пользователя через админку и активирует ему TFA через браузер.

    Возвращает (username, password, totp_secret, user_id).
    """
    import pyotp
    from playwright.sync_api import sync_playwright
    from utils.config import BASE_URL

    username, password, user_id = create_fresh_tfa_user()
    secret = None

    def _run():
        nonlocal secret
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(f"{BASE_URL}/login", wait_until="networkidle")
            page.locator("input[name=username]").fill(username)
            page.locator("input[name=password]").fill(password)
            page.locator("button[type=submit]").click()
            page.wait_for_url(
                lambda url: "dashboard" in url or "tfa/setup" in url or "tfa/verify" in url,
                timeout=30000,
            )
            if "tfa/setup" not in page.url:
                page.goto(f"{BASE_URL}/tfa/setup", wait_until="networkidle", timeout=30000)
            secret_locator = page.locator("text=/(?:[A-Z2-7]{4} *){3,}/")
            secret_locator.wait_for(state="visible", timeout=10000)
            secret = secret_locator.inner_text().strip().replace(" ", "")
            code = pyotp.TOTP(secret).now()
            page.locator("input[name='key']").fill(code)
            page.get_by_role("button", name="Подключить").click()
            page.wait_for_url("**/dashboard**", timeout=15000)
            browser.close()

        import time
        # The activation code was just used — wait for the next TOTP window
        # so any subsequent verify_tfa call uses a fresh, unreused code.
        remaining = 30 - (time.time() % 30)
        time.sleep(remaining + 1)

    t = threading.Thread(target=_run)
    t.start()
    t.join()
    return username, password, secret, user_id


def delete_user(user_id: int) -> None:
    """Удаляет пользователя по ID через админку.

    Запускается в отдельном потоке — вне asyncio-цикла pytest-playwright.
    """
    def _run():
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    page = browser.new_page()
                    _do_admin_login(page, ADMIN_URL, ADMIN_USER, ADMIN_PASSWORD)
                    page.goto(f"{ADMIN_URL}/core/user/{user_id}/delete/")
                    page.wait_for_load_state("networkidle")
                    _remove_debug_toolbar(page)
                    page.wait_for_function(
                        "() => !!document.querySelector('form')", timeout=10000
                    )
                    page.evaluate("document.querySelector('form').submit()")
                    page.wait_for_load_state("networkidle")
                finally:
                    browser.close()
        except Exception as exc:
            import warnings
            warnings.warn(f"delete_user({user_id}) failed: {exc}")

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=60)
