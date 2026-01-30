import os
import time
import datetime
import warnings

import pytest
import allure
from PIL import ImageGrab
from allure_commons.types import AttachmentType

from pages.base_page import BasePage
from config.logger import get_logger

import pythoncom  # ✅ added

SCREENSHOT_DIR = "screenshots"
LOG_FILE = os.path.join("logs", "execution.log")

log = get_logger("pytest")

# =================================================
# WARNINGS
# =================================================
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="pywinauto")
warnings.filterwarnings("ignore", category=UserWarning, module="PIL")


# =================================================
# COM INIT (Recommended for pywinauto UIA stability)
# =================================================
@pytest.fixture(scope="session", autouse=True)
def init_com():
    pythoncom.CoInitialize()
    yield
    pythoncom.CoUninitialize()


# =================================================
# APP FIXTURE  ✅ changed to function scope
# =================================================
@pytest.fixture()
def app():
    page = BasePage()
    yield page
    page.kill()


# =================================================
# TIMER
# =================================================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    item._start = time.time()
    yield


# =================================================
# REPORT + SCREENSHOT
# =================================================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when != "call":
        return

    duration = time.time() - getattr(item, "_start", time.time())

    allure.attach(
        f"{duration:.2f}s",
        "Test Duration",
        AttachmentType.TEXT
    )

    log.info("%s took %.2fs", item.nodeid, duration)

    if rep.failed:
        _screenshot(item)


def _screenshot(item):
    try:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        img = ImageGrab.grab(all_screens=True)
        path = os.path.join(SCREENSHOT_DIR, f"{item.name}_{ts}.png")
        img.save(path)

        # ✅ attach the saved png file (correct)
        with open(path, "rb") as f:
            allure.attach(f.read(), "Failure Screenshot", AttachmentType.PNG)

    except Exception as e:
        log.error("Screenshot failed: %s", e)


# =================================================
# LOG ATTACHMENT
# =================================================
@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            allure.attach(f.read(), "Execution Log", AttachmentType.TEXT)

    time.sleep(1)


# =================================================
# WAIT HELPER
# =================================================
def ui_step_wait():
    time.sleep(1)
