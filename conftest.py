import os
import time
import datetime
import warnings
import json
import platform
import sys

import pytest
import allure
import pythoncom
from PIL import ImageGrab
from allure_commons.types import AttachmentType
from datetime import datetime

from pages.base_page import BasePage
from config.logger import get_logger


# =================================================
# CONSTANTS
# =================================================

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
# COM INIT (pywinauto UIA stability)
# =================================================

@pytest.fixture(scope="session", autouse=True)
def init_com():
    pythoncom.CoInitialize()
    yield
    pythoncom.CoUninitialize()


# =================================================
# APP FIXTURE (function scoped – safer for Desktop UI)
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
# REPORT + SCREENSHOT + DURATION
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
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        img = ImageGrab.grab(all_screens=True)
        path = os.path.join(SCREENSHOT_DIR, f"{item.name}_{ts}.png")
        img.save(path)

        # Attach saved PNG to Allure
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


# =================================================
# ALLURE ENVIRONMENT.PROPERTIES
# =================================================

@pytest.fixture(scope="session", autouse=True)
def create_environment_file(request):
    allure_dir = request.config.getoption('--alluredir')

    if allure_dir:
        env_file = os.path.join(allure_dir, 'environment.properties')

        with open(env_file, 'w') as f:
            # System
            f.write(f"OS={platform.system()} {platform.release()}\n")
            f.write(f"OS.Version={platform.version()}\n")
            f.write(f"Architecture={platform.machine()}\n")
            f.write(f"Hostname={platform.node()}\n")
            f.write(f"Computer.Name={os.environ.get('COMPUTERNAME', 'Unknown')}\n")
            f.write(f"User={os.environ.get('USERNAME', 'Unknown')}\n\n")

            # Python
            f.write(f"Python.Version={sys.version.split()[0]}\n")
            f.write(f"Pytest.Version={pytest.__version__}\n")
            f.write(f"Python.Path={sys.executable}\n\n")

            # Test Environment
            f.write("Environment=QA\n")
            f.write("Application=InstantInk WJA Desktop\n")
            f.write("Application.Version=1.0.0\n")
            f.write("Test.Suite=POC Smoke Tests\n")
            f.write("Test.Framework=Pytest + Allure\n\n")

            # Execution
            f.write("Test.Executor=Windows Task Scheduler\n")
            f.write("Execution.Mode=Automated\n")
            f.write(f"Execution.Date={datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"Execution.Time={datetime.now().strftime('%H:%M:%S')}\n")
            f.write(f"Execution.Timestamp={datetime.now().isoformat()}\n")


# =================================================
# ALLURE EXECUTOR.JSON
# =================================================

@pytest.fixture(scope="session", autouse=True)
def create_executor_file(request):
    allure_dir = request.config.getoption('--alluredir')

    if allure_dir:
        executor_file = os.path.join(allure_dir, 'executor.json')
        build_number = datetime.now().strftime('%Y%m%d%H%M%S')

        executor_info = {
            "name": "Windows Task Scheduler",
            "type": "local",
            "url": "http://localhost",
            "buildOrder": int(build_number),
            "buildName": f"Automated Test Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "buildUrl": f"file:///{os.getcwd().replace(os.sep, '/')}",
            "reportUrl": f"file:///{os.path.join(os.getcwd(), 'reports').replace(os.sep, '/')}",
            "reportName": f"Allure Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "executionDate": datetime.now().isoformat()
        }

        with open(executor_file, 'w') as f:
            json.dump(executor_info, f, indent=2)


# =================================================
# ALLURE DYNAMIC LABELS PER TEST
# =================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        allure.dynamic.label("host", platform.node())
        allure.dynamic.label("os", platform.system())
