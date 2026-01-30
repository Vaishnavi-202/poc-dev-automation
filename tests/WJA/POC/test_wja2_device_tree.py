import allure
import pytest
from pages.device_management.base_page import DeviceManagementBasePage

@allure.title("Verify navigation of WJA device tree items")
@pytest.mark.desktop
def test_device_navigation_tree_items(app):

    # Instantiate the unified page
    dm_page = DeviceManagementBasePage(app)

    with allure.step("Navigate through all device tree nodes"):
        dm_page.click_all_devices()
        dm_page.click_error_devices()
        dm_page.click_warning_devices()
        dm_page.click_new_devices()
        dm_page.click_ungrouped_devices()