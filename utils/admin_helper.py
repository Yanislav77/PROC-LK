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


def delete_user(user_id: int) -> None:
    """Удаляет пользователя по ID через админку.

    Запускается в отдельном потоке — вне asyncio-цикла pytest-playwright.
    """
    def _run():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            _do_admin_login(page, ADMIN_URL, ADMIN_USER, ADMIN_PASSWORD)

            page.goto(f"{ADMIN_URL}/core/user/{user_id}/delete/")
            page.wait_for_load_state("networkidle")
            _remove_debug_toolbar(page)
            page.locator("input[type=submit], button[type=submit]").first.click()
            page.wait_for_load_state("networkidle")

            browser.close()

    t = threading.Thread(target=_run)
    t.start()
    t.join()
