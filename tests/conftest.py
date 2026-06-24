"""
Общий conftest для всех тестов: HTML-отчёт с описаниями и скриншотами.

Показывает docstring теста для:
  - call   — сам тест (pass / fail)
  - setup  — когда тест упал ещё в фикстуре (Error)
"""
import base64
import html as _html
import re
from pathlib import Path

import pytest
import pytest_html

SCREENSHOTS_DIR = Path("reports/screenshots")


def _safe_name(nodeid: str) -> str:
    parts = nodeid.split("::")
    name_parts = [p for p in parts[1:] if p]
    name = "__".join(name_parts[-2:] if len(name_parts) >= 2 else name_parts[-1:])
    name = re.sub(r"\[.*?\]", "", name)
    return re.sub(r"[^\w]", "_", name)[:120]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Описание теста и скриншот при падении — прикрепляет к HTML-отчёту."""
    outcome = yield
    report = outcome.get_result()

    if report.when not in ("call", "setup"):
        return

    report.extras = getattr(report, "extras", [])
    description = (item.function.__doc__ or "").strip()

    if report.when == "setup" and report.failed:
        label = "<b>&#9888; Ошибка в фикстуре (setup) — тест не запустился</b>"
        if description:
            label += f"<br><i>Тест проверял:</i> {_html.escape(description)}"
        report.extras.insert(0, pytest_html.extras.html(f"<p>{label}</p>"))
        return

    if description:
        report.extras.insert(0, pytest_html.extras.html(f"<p>{_html.escape(description)}</p>"))

    if not report.failed:
        return

    # Скриншот — только для UI-тестов (page-фикстура есть только у Playwright)
    page = item.funcargs.get("page")
    if page is None:
        return
    try:
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        path = SCREENSHOTS_DIR / f"{_safe_name(item.nodeid)}.png"
        raw = page.screenshot(path=str(path), full_page=True)
        b64 = base64.b64encode(raw).decode("utf-8")
        report.extras.append(
            pytest_html.extras.image(f"data:image/png;base64,{b64}", name="screenshot")
        )
    except Exception:
        pass
