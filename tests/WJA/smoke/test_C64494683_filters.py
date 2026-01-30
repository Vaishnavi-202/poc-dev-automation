import pytest
import allure
from pages.device_management.all_devices_page import AllDevicesPage

@allure.title("C64494683 - Verify Filter Creation and Management")
@allure.description("Tests creating a new filter using legacy logic wrapped in new framework.")
@pytest.mark.desktop
def test_filters(app):
    
    # Initialize
    filter_page = AllDevicesPage(app)

    # 1. Open Panel
    with allure.step("Open Filters Panel"):
        filter_page.open_filters_panel()

    # 2. Create New Filter
    with allure.step("Create New Filter (Legacy Keys)"):
        # This calls: Tab 5 -> Enter, Wait 4s -> Enter, Fills Dialog
        filter_page.create_new_filter(
            property_name="Device Groups", 
            value="123",
            function="Contains"
        )

    # 3. Save Step 1
    with allure.step("Click OK (1)"):
        filter_page.save_filter_step_1()

    # 4. Edit / Select Row
    with allure.step("Select Last Row"):
        filter_page.select_last_filter_row()
        filter_page.save_filter_final() # Click OK (0)

    # 5. Remove Sequence
    with allure.step("Remove Filter Sequence"):
        filter_page.open_filters_panel() # Reset focus
        filter_page.remove_selected_filter() # Calls Tab 3, Select Row, Remove, Cancel

    # 6. Final Sequence (click_new3)
    with allure.step("Final Sequence"):
        filter_page.open_filters_panel()
        filter_page.context_menu_action_3()