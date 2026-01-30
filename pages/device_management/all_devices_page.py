import time
from pywinauto.keyboard import send_keys
from pywinauto import timings

# ✅ Inherit from your new Module Base Page
from pages.device_management.base_page import DeviceManagementBasePage
from conftest import ui_step_wait
from config.logger import get_logger

log = get_logger(__name__)


class AllDevicesPage(DeviceManagementBasePage):
    """
    Page Object for the 'All Devices' view (Right Side Panel).
    Formatted in the New Framework structure but uses Legacy Logic (send_keys)
    for robustness where UIA fails.
    """

    # Timings from your old code
    timings.Timings.after_clickinput_wait = 0
    timings.Timings.after_setfocus_wait = 0
    timings.Timings.window_find_timeout = 1

    # -------------------------------------------------
    # ELEMENT GETTERS
    # -------------------------------------------------

    def _filters_button(self):
        return self.main_window.child_window(title="Filters", control_type="Button")

    def _filter_dialog(self):
        """
        Uses app.top_window() as per your working legacy code.
        """
        dlg = self.app.top_window()
        dlg.wait("exists visible", timeout=60)
        return dlg

    # --- Dialog Elements ---

    def _device_group_combo(self, dlg):
        return dlg.child_window(title="Device Groups", control_type="ComboBox")
    
    def _filter_function_combo(self, dlg):
        return dlg.child_window(title="Filter Function", control_type="ComboBox")

    def _value_edit(self, dlg):
        return dlg.child_window(title="Value", control_type="Edit")

    def _options_combo(self, dlg):
        return dlg.child_window(title="Options", control_type="ComboBox")

    def _ok_button(self, dlg, index=0):
        return dlg.child_window(title="OK", control_type="Button", found_index=index)

    def _cancel_button(self, dlg, index=0):
        return dlg.child_window(title="Cancel", control_type="Button", found_index=index)

    def _remove_button(self, dlg):
        return dlg.child_window(title="Remove", control_type="Button")

    def _data_grid(self, dlg):
        return dlg.child_window(control_type="DataGrid")

    # -------------------------------------------------
    # LOW LEVEL ACTIONS
    # -------------------------------------------------

    def _click_filters_panel(self):
        log.info("Clicking 'Filters' button on panel")
        self.focus_window()
        self._filters_button().wait("visible enabled", timeout=25).click_input()
        ui_step_wait()

    # --- Context Menu / Keyboard Nav (Legacy Logic) ---

    def _keyboard_nav_tab_5_enter(self):
        """Corresponds to old 'click_new'"""
        log.info("Keyboard: {TAB 5}{ENTER}")
        self.focus_window()
        send_keys("{TAB 5}{ENTER}")

    def _keyboard_nav_tab_3_enter(self):
        """Corresponds to old 'click_new2'"""
        log.info("Keyboard: {TAB 3}{ENTER}")
        self.focus_window()
        send_keys("{TAB 3}{ENTER}")
    
    def _keyboard_nav_tab_2_enter(self):
        """Corresponds to old 'click_new3'"""
        log.info("Keyboard: {TAB 2}{ENTER}")
        self.focus_window()
        send_keys("{TAB 2}{ENTER}")
        time.sleep(10) # Preserving your explicit sleep

    def _keyboard_select_add(self):
        """Corresponds to old 'click_add'"""
        log.info("Keyboard: Wait 4s -> {ENTER} (Select Add)")
        time.sleep(4)
        send_keys("{ENTER}")

    # --- Dialog Actions ---

    def _set_device_property(self, dlg, value):
        combo = self._device_group_combo(dlg)
        combo.wait("visible enabled ready", timeout=10)
        combo.click_input()
        send_keys(value)
        send_keys("{ENTER}")

    def _set_filter_function(self, dlg, func_type="Contains"):
        combo = self._filter_function_combo(dlg)
        combo.wait("visible enabled ready", timeout=10)
        combo.select(func_type)

    def _set_value(self, dlg, value):
        edit = self._value_edit(dlg)
        edit.wait("visible ready", timeout=10)
        edit.set_edit_text(value)

    def _set_options(self, dlg, option="Ignore Case"):
        combo = self._options_combo(dlg)
        combo.wait("visible enabled ready", timeout=10)
        combo.select(option)

    def _click_ok(self, dlg, index=0):
        btn = self._ok_button(dlg, index)
        btn.wait("visible enabled ready", timeout=30)
        btn.click_input()

    def _click_cancel(self, dlg, index=0):
        btn = self._cancel_button(dlg, index)
        btn.wait("visible enabled ready", timeout=30)
        btn.click_input()

    def _click_remove(self, dlg):
        time.sleep(2)
        btn = self._remove_button(dlg)
        btn.wait("visible enabled", timeout=30)
        btn.click_input()
        time.sleep(9) # Preserving your explicit sleep

    def _select_last_grid_row(self, dlg):
        """
        Logic to find and click the last row in Device Property column.
        """
        log.info("Selecting last row in 'Device Property'")
        header = dlg.child_window(title="Device Property", control_type="Header")
        header.wait("exists visible", timeout=10)
        
        # Calculate column bounds
        header_rect = header.rectangle()
        col_left, col_right = header_rect.left, header_rect.right

        items = dlg.descendants(control_type="DataItem")
        
        # Filter items in the column
        col_items = []
        for item in items:
            r = item.rectangle()
            center_x = (r.left + r.right) // 2
            if col_left <= center_x <= col_right:
                col_items.append(item)

        if not col_items:
            # Fallback or specific logic if grid is empty
            log.warning("No items found in Device Property column to select.")
            return

        # Sort by Y position
        col_items.sort(key=lambda x: x.rectangle().top)
        
        # Click the last one
        last_cell = col_items[-1]
        rect = last_cell.rectangle()
        last_cell.click_input(coords=(rect.width() // 2, rect.height() // 2))

    # -------------------------------------------------
    # HIGH LEVEL FLOWS (PUBLIC API)
    # -------------------------------------------------

    def open_filters_panel(self):
        """Ensures All Devices is selected, then opens Filters panel."""
        self.click_all_devices()
        self._click_filters_panel()

    def create_new_filter(self, property_name, value, function="Contains", ignore_case=True):
        """
        High level flow to add a filter.
        Uses the legacy Tab/Enter sequences mapped to actions.
        """
        # 1. Open Context Menu (Tab 5 -> Enter)
        self._keyboard_nav_tab_5_enter()
        
        # 2. Select Add (Sleep 4 -> Enter)
        self._keyboard_select_add()

        # 3. Fill Dialog
        dlg = self._filter_dialog()
        # Set focus to ensure stability
        dlg.set_focus()

        self._set_device_property(dlg, property_name)
        self._set_filter_function(dlg, function)
        self._set_value(dlg, value)
        
        if ignore_case:
            self._set_options(dlg, "Ignore Case")

    def save_filter_step_1(self):
        """Clicks the first OK button (e.g. adding rule to list)"""
        dlg = self._filter_dialog()
        self._click_ok(dlg, index=1)

    def save_filter_final(self):
        """Clicks the final OK button to close dialog"""
        dlg = self._filter_dialog()
        self._click_ok(dlg, index=0)

    def select_last_filter_row(self):
        dlg = self._filter_dialog()
        self._select_last_grid_row(dlg)

    def remove_selected_filter(self):
        """
        High level flow to remove a filter.
        """
        # 1. Open Context Menu (Tab 3 -> Enter) - assuming this maps to 'click_new2'
        self._keyboard_nav_tab_3_enter()
        
        # 2. Select the row
        dlg = self._filter_dialog()
        self._select_last_grid_row(dlg)

        # 3. Click Remove
        self._click_remove(dlg)
        
        # 4. Click Cancel (index 0) as per your old 'click_on_ok_btn5' logic
        self._click_cancel(dlg, index=0)

    def context_menu_action_3(self):
        """Legacy click_new3"""
        self._keyboard_nav_tab_2_enter()
        