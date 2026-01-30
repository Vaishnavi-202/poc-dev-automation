from pages.base_page import BasePage
from conftest import ui_step_wait
from config.logger import get_logger

log = get_logger(__name__)


class DeviceManagementBasePage(BasePage):
    """
    The Single Source of Truth for the Device Management Module.
    
    Functionality:
    1. Auto-clicks 'Device Management' main tab on initialization.
    2. Provides built-in methods to navigate the Left Dock Tree (Overview, Groups, All Devices).
    """

    # -------------------------------------------------
    # CONSTANTS (Tree Paths)
    # -------------------------------------------------
    PATHS = {
        # Navigation Items
        "Overview": r"\Overview",
        "Groups": r"\Groups",
        "Discovery": r"\Discovery",
        "Configuration": r"\Configuration",
        
        # Device Filters
        "All Devices": r"\All Devices",
        "Error Devices": r"\Error Devices",
        "Warning Devices": r"\Warning Devices",
        "New Devices": r"\New (Last Discovery)",
        "Ungrouped Devices": r"\Ungrouped Devices",
    }

    def __init__(self, app):
        super().__init__(app)
        self._ensure_module_active()

    # -------------------------------------------------
    # MODULE SELECTION (Top Tab)
    # -------------------------------------------------

    def _device_management_btn(self):
        return self.main_window.child_window(title="Device Management", control_type="Button")

    def _ensure_module_active(self):
        """Clicks the 'Device Management' tab to ensure we are in the right view."""
        log.info("Ensuring 'Device Management' module is active...")
        try:
            self._device_management_btn().click()
            ui_step_wait()
        except Exception as e:
            # It might already be selected or strictly not found, log but proceed
            log.warning(f"Note: Device Management button check: {e}")

    # -------------------------------------------------
    # TREE CONTROL (Left Dock)
    # -------------------------------------------------

    def _tree_control(self):
        """
        Resolves the parent TreeView by first finding the 'Overview' item.
        This is robust against window resizing or different layouts.
        """
        overview = self.main_window.child_window(title="Overview", control_type="TreeItem")
        overview.wait("exists", timeout=15)
        return overview.parent()

    def _get_tree_item(self, path_key):
        """Gets a specific node using the robust get_item method (handles off-screen)."""
        path = self.PATHS.get(path_key)
        tree = self._tree_control()
        return tree.get_item(path)

    def _select_node(self, path_key):
        """Generic internal method to select a tree node."""
        log.info(f"Navigating Tree: {path_key}")
        item = self._get_tree_item(path_key)
        item.select()
        ui_step_wait()

    # -------------------------------------------------
    # PUBLIC API (Navigation)
    # -------------------------------------------------

    # --- Main Sections ---
    def click_overview(self):
        self._select_node("Overview")

    def click_groups(self):
        self._select_node("Groups")

    def click_discovery(self):
        self._select_node("Discovery")

    def click_configuration(self):
        self._select_node("Configuration")

    # --- Device Filters ---
    def click_all_devices(self):
        self._select_node("All Devices")

    def click_error_devices(self):
        self._select_node("Error Devices")

    def click_warning_devices(self):
        self._select_node("Warning Devices")

    def click_new_devices(self):
        self._select_node("New Devices")

    def click_ungrouped_devices(self):
        self._select_node("Ungrouped Devices")