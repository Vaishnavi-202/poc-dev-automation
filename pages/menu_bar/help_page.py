from pywinauto.keyboard import send_keys
from pages.base_page import BasePage
from config.logger import get_logger
from conftest import ui_step_wait

log = get_logger(__name__)


class HelpPage(BasePage):

    # -------------------------------------------------
    # LOW LEVEL ACTIONS
    # -------------------------------------------------

    def _press_help_menu(self):
        send_keys("%H")
        ui_step_wait()
        log.info("Pressed Help menu")

    def _press_about(self):
        send_keys("A")
        ui_step_wait()
        log.info("Pressed About")

    def _open_about_details(self):
        send_keys("{TAB}{ENTER}")
        ui_step_wait()
        log.info("Opened About details")

    def _close_about_details(self):
        send_keys("{ENTER}{TAB}{TAB}{ENTER}")
        ui_step_wait()
        log.info("Closed About details")

    # -------------------------------------------------
    # PAGE VALIDATION
    # -------------------------------------------------

    def is_launched(self):
        self.main_window.wait("visible", timeout=30)
        log.info("WJA main window is visible")
        return True

    # -------------------------------------------------
    # SINGLE HIGH LEVEL FLOW (ONLY ONE TEST USES THIS)
    # -------------------------------------------------

    def open_about_and_close_details(self):
        self.focus_window()
        self._press_help_menu()
        self._press_about()
        self._open_about_details()
        self._close_about_details()
        log.info("Completed About flow")
