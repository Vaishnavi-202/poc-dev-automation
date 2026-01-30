import allure
from pages.device_management.group_page import NavigationPage

@allure.title("Create and delete group from WJA navigation")
def test_create_and_delete_group(app):

    nav = NavigationPage(app)

    with allure.step("Create new group"):
        nav.open_overview_and_groups()
        nav.click_create_group()
        nav.create_group("test_1")

    with allure.step("Select and delete created group"):
        nav.select_group("test_1")
        nav.delete_group()
