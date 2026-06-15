import re
import shutil
import subprocess
import time
from pathlib import Path
import pytest
from utils.config import HEADLESS, VIDEO, TEST_USER_EMAIL, TEST_USER_PASSWORD
from api_clients.auth_client import AuthClient

VIDEO_DIR = Path("reports/videos")

# Видео текущего прогона в порядке выполнения тестов
_session_videos: list[Path] = []


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    args = {**browser_context_args, "viewport": {"width": 1440, "height": 900}}
    if VIDEO:
        VIDEO_DIR.mkdir(parents=True, exist_ok=True)
        args["record_video_dir"] = str(VIDEO_DIR)
        args["record_video_size"] = {"width": 1440, "height": 900}
    return args


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Переименовывает видео после полного закрытия контекста (when=teardown)."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "teardown":
        return
    src_str = getattr(item, "_video_src", None)
    name = getattr(item, "_video_name", None)
    if not src_str or not name:
        return
    src = Path(src_str)
    dst = src.parent / f"{name}.webm"
    for _ in range(20):
        if src.exists():
            try:
                src.replace(dst)   # replace() перезаписывает существующий файл на Windows
                _session_videos.append(dst)
            except OSError:
                pass
            break
        time.sleep(0.1)


def pytest_sessionfinish(session, exitstatus):
    """После прогона склеивает все видео текущей сессии в один файл."""
    if not VIDEO or len(_session_videos) < 2:
        return
    if not shutil.which("ffmpeg"):
        print("\nffmpeg не найден — склейка видео пропущена.")
        return

    filelist = VIDEO_DIR / "_filelist.txt"
    filelist.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in _session_videos),
        encoding="utf-8",
    )

    output = VIDEO_DIR / "all_tests.webm"
    result = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(filelist), "-c", "copy", str(output)],
        capture_output=True,
    )
    filelist.unlink(missing_ok=True)

    if result.returncode == 0:
        print(f"\nВидео сессии сохранено: {output}")
    else:
        print(f"\nОшибка склейки видео: {result.stderr.decode()}")


@pytest.fixture(scope="session")
def launch_browser_args():
    return {"headless": HEADLESS}


@pytest.fixture(scope="session")
def auth_token():
    client = AuthClient()
    response = client.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    response.raise_for_status()
    return response.json()["response"]["access"]


@pytest.fixture
def api_client(auth_token):
    return AuthClient(token=auth_token)
