import allure
import pytest
from pages.device_management.base_page import DeviceManagementBasePage

@allure.title("Verify main navigation tabs in WJA")
# @pytest.mark.desktop  <-- Uncomment if you have this marker registered in pytest.ini
def test_quick_device_discovery(app):

    # Instantiate the unified page
    dm_page = DeviceManagementBasePage(app)

    with allure.step("Navigate through main menu sections"):
        dm_page.click_overview()
        dm_page.click_groups()
        dm_page.click_discovery()
        dm_page.click_configuration()
    