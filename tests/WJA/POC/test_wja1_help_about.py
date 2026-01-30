from pages.menu_bar.help_page import HelpPage

def test_help_about_flow():
    main = HelpPage()

    # Single combined flow
    main.open_about_and_close_details()
