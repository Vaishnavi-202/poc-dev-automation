from pages.device_management.base_page import DeviceManagementBasePage
from conftest import ui_step_wait
from config.logger import get_logger

log = get_logger(__name__)


# ✅ Inherit from DeviceManagementBasePage to use the robust "Overview/Groups" logic
class NavigationPage(DeviceManagementBasePage):

    # -------------------------------------------------
    # ELEMENT GETTERS (Group Specific Only)
    # -------------------------------------------------
    
    # Note: _overview_item and _groups_item are removed 
    # because they are handled by the parent class.

    def _create_group_btn(self):
        return self.main_window.child_window(auto_id="button_create", control_type="Button")

    def _delete_group_btn(self):
        return self.main_window.child_window(auto_id="button_delete", control_type="Button")

    def _group_tree_item(self, group_name):
        return self.main_window.child_window(title=group_name, control_type="TreeItem")

    # ---- Create Group Dialog ----

    def _create_group_dialog(self):
        dlg = self.app.window(title_re="Create Group.*")
        dlg.wait("exists", timeout=5)
        return dlg

    def _new_group_name_edit(self, dlg):
        return dlg.child_window(auto_id="textBox_newGroupName", control_type="Edit")

    def _dlg_next_btn(self, dlg):
        return dlg.child_window(auto_id="btnNext")

    def _dlg_done_btn(self, dlg):
        return dlg.child_window(auto_id="btnDone")

    # ---- Delete Group Dialog ----

    def _delete_group_dialog(self):
        dlg = self.app.window(title_re="Delete Group.*")
        dlg.wait("exists", timeout=5)
        return dlg

    # -------------------------------------------------
    # LOW LEVEL ACTIONS
    # -------------------------------------------------

    # Note: _select_overview and _select_groups are removed.

    def _click_create_group(self):
        self._create_group_btn().click()
        ui_step_wait()

    def _enter_group_name(self, group_name):
        dlg = self._create_group_dialog()
        self._new_group_name_edit(dlg).set_edit_text(group_name)

    def _click_dialog_next(self, dlg):
        self._dlg_next_btn(dlg).click()
        ui_step_wait()

    def _click_dialog_done(self, dlg):
        self._dlg_done_btn(dlg).click()
        ui_step_wait()

    def _select_group_item(self, group_name):
        self._group_tree_item(group_name).select()
        ui_step_wait()

    def _click_delete_group(self):
        self._delete_group_btn().click()
        ui_step_wait()

    # -------------------------------------------------
    # HIGH LEVEL FLOWS (PUBLIC API)
    # -------------------------------------------------

    def open_overview_and_groups(self):
        # ✅ Uses robust methods from DeviceManagementBasePage
        self.click_overview()
        self.click_groups()

    def click_create_group(self):
        self._click_create_group()

    def create_group(self, group_name):
        self._enter_group_name(group_name)

        dlg = self._create_group_dialog()
        self._click_dialog_next(dlg)
        self._click_dialog_next(dlg)
        self._click_dialog_done(dlg)

    def select_group(self, group_name):
        self._select_group_item(group_name)

    def delete_group(self):
        self._click_delete_group()

        dlg = self._delete_group_dialog()
        self._click_dialog_next(dlg)
        self._click_dialog_done(dlg)