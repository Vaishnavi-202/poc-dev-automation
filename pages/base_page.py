import time
from pywinauto import Application, Desktop
from pywinauto.keyboard import send_keys
from pywinauto.timings import wait_until_passes
from pywinauto.findwindows import ElementNotFoundError

from config.logger import get_logger
from config.config_parser import load_config

log = get_logger(__name__)

# Load config once
config = load_config()


class BasePage:
    """
    Base page that manages WJA application lifecycle.

    RULE:
    - If WJA was already open -> connect -> DO NOT close it
    - If automation launches WJA -> owns it -> MUST close it in teardown
    """

    # =================================================
    # CONFIG
    # =================================================
    WJA_EXE_PATH = config.get("WJA_EXE_PATH")

    _raw_title = config.get("WJA_TITLE")
    WINDOW_TITLE_REGEX = rf"{_raw_title}$"

    MAIN_WINDOW_TIMEOUT = 40
    RETRY_INTERVAL = 1

    INSECURE_TIMEOUT = 30
    RUN_DISCOVERY_TIMEOUT = 40

    def __init__(self, app=None):
        """
        app can be:
        - None -> launch/connect internally
        - BasePage instance OR Application instance passed from pytest fixture
        """
        if app:
            # app may be BasePage wrapper or raw Application
            self.app = app.app if hasattr(app, "app") else app
            self._owns_app = False
            log.info("Using app from pytest fixture (not owner)")
        else:
            self.app, self._owns_app = self._launch_or_connect()

        # ✅ IMPORTANT: Don't cache main window across tests.
        self.main_window = self._resolve_main_window()

    # =================================================
    # Launch OR Connect
    # =================================================

    def _launch_or_connect(self):
        """
        Connect to existing WJA if exists, otherwise launch fresh.

        Returns:
            (app, owns_app)
            owns_app=True  => started new instance
            owns_app=False => connected to existing instance
        """
        app = Application(backend="uia")
        desktop = Desktop(backend="uia")

        # Try to connect if already running
        try:
            if desktop.window(title_re=self.WINDOW_TITLE_REGEX).exists(timeout=2):
                app.connect(title_re=self.WINDOW_TITLE_REGEX)
                log.info("✅ Connected to existing HP Web Jetadmin instance")
                return app, False
        except Exception as e:
            log.warning(f"Connect attempt failed (will launch fresh): {e}")

        # Launch fresh
        log.info("🚀 No existing instance found. Launching fresh WJA...")
        app.start(self.WJA_EXE_PATH)

        # Handle popups
        self._handle_insecure_popup(desktop)
        self._handle_run_discovery_popup(desktop)

        # Reconnect to UI
        app.connect(title_re=self.WINDOW_TITLE_REGEX, timeout=30)
        log.info("✅ HP Web Jetadmin launched and ready")

        return app, True

    # =================================================
    # Popup Handling
    # =================================================

    def _handle_insecure_popup(self, desktop):
        for _ in range(self.INSECURE_TIMEOUT):
            try:
                dlg = desktop.window(title_re=".*In-Secure Connection.*")
                if dlg.exists(timeout=1):
                    dlg.set_focus()
                    time.sleep(1)
                    try:
                        dlg.child_window(title="Yes", control_type="Button").invoke()
                    except Exception:
                        send_keys("{ENTER}")
                    log.info("✅ Handled In-Secure Connection popup")
                    return
            except Exception:
                pass
            time.sleep(1)

    def _handle_run_discovery_popup(self, desktop):
        for _ in range(self.RUN_DISCOVERY_TIMEOUT):
            try:
                dlg = desktop.window(title_re=".*Run Discovery.*")
                if dlg.exists(timeout=1):
                    dlg.set_focus()
                    time.sleep(1)

                    send_keys("{TAB}")
                    time.sleep(0.5)
                    send_keys("{ENTER}")

                    log.info("✅ Handled Run Discovery popup")
                    return
            except Exception:
                pass
            time.sleep(1)

    # =================================================
    # Main Window Resolution
    # =================================================

    def _resolve_main_window(self):
        log.info("Resolving main window via Desktop search...")

        def _get_window():
            win = Desktop(backend="uia").window(title_re=self.WINDOW_TITLE_REGEX)
            win.wait("exists visible enabled", timeout=5)
            return win

        return wait_until_passes(
            timeout=self.MAIN_WINDOW_TIMEOUT,
            retry_interval=self.RETRY_INTERVAL,
            func=_get_window,
            exceptions=(ElementNotFoundError, Exception),
        )

    # =================================================
    # Utility
    # =================================================

    def focus_window(self):
        if not self.main_window:
            return
        try:
            if self.main_window.get_show_state() == 2:
                self.main_window.restore()
            self.main_window.set_focus()
        except Exception as e:
            log.warning(f"Could not focus window: {e}")

    # =================================================
    # Kill / Cleanup
    # =================================================

    def kill(self):
        """
        Close WJA only if automation launched it.
        """
        if not getattr(self, "_owns_app", False):
            log.info("WJA was already running — skipping kill")
            return

        log.info("🛑 Closing HP Web Jetadmin (launched by automation)...")
        try:
            if self.app:
                self.app.kill()
                log.info("✅ WJA closed successfully")
        except Exception as e:
            log.warning(f"Failed to kill WJA: {e}")
        finally:
            # reset window pointer to avoid stale objects
            self.main_window = None
