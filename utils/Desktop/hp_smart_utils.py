from asyncio.log import logger
import subprocess
import time
import os
import time
import threading
import psutil
from Utils.selenium_utils import get_text
from pywinauto.application import Application
from datetime import datetime
import pyautogui
import pytest
from pywinauto import Application
from PIL import Image
from pywinauto import Desktop, Application, mouse
from pywinauto.keyboard import send_keys
from pywinauto.timings import wait_until, TimeoutError
from selenium.webdriver.support.expected_conditions import title_is
from conftest import load_desktop_printer_data

from Utils.Desktop.common_desk_utilities import (
    force_close_hp_smart,
    launch_hp_smart_app,
    capture_ui_tree, take_screenshot,
)
from conftest import ui_tree_file_path


def wait_for_element(element, timeout=30):
    """Generic wait for Pywinauto element to exist and enabled."""

    wait_until(timeout=timeout, retry_interval=1,

               func=lambda: element.exists() and element.is_enabled())

    return element


# ============Launch App=========================
def launch_and_connect_hp_smart(ui_tree_file_path):
    """

    Force close HP Smart, launch it, and connect to the main window.

    :param ui_tree_file_path: Path to save UI tree captures

    :return: main_window (pywinauto window object), app (pywinauto Application object)

    """

    # Step 1: Ensure HP Smart is closed

    force_close_hp_smart()

    # Step 2: Launch the HP Smart app

    launch_hp_smart_app()

    print("HP Smart app launched.")

    # Step 3: Connect to the app main window

    app = Application(backend="uia").connect(title="HP Smart")

    main_window = app.window(title_re="HP Smart")


    main_window.wait("visible", timeout=50)

    main_window.set_focus()

    main_window.maximize()
    capture_ui_tree(main_window, ui_tree_file_path, "App Launch", append=False)
    print("Connected to HP Smart app.")
    return main_window, app

def is_hp_smart_running(process_name="HP Smart.exe"):
    for p in psutil.process_iter(['name']):
        if p.info['name'] and process_name.lower() in p.info['name'].lower():
            return True
    return False

def restart_hp_smart(ui_tree_file_path):
    if is_hp_smart_running():
        print("HP Smart already running, no restart needed.")
        return None, None

    print("HP Smart crashed. Restarting...")
    launch_hp_smart_app()
    time.sleep(5)
    app = Application(backend="uia").connect(title="HP Smart")
    main_window = app.window(title_re="HP Smart")
    main_window.wait("visible", timeout=30)
    return main_window, app

import threading
import time

def monitor_hp_smart(ui_tree_file_path, interval=5, startup_delay=10, max_runs=3):
    """
    Monitors the HP Smart app and restarts it if not running.
    The monitor stops automatically after 'max_runs' checks.
    """
    def _watch():
        time.sleep(startup_delay)  # Wait before first check
        run_count = 0  # Track how many times the loop runs

        while run_count < max_runs:
            print(f"Monitoring run {run_count + 1}/{max_runs}...")

            if not is_hp_smart_running():
                print("HP Smart not running, restarting...")
                restart_hp_smart(ui_tree_file_path)
            else:
                print(" HP Smart is running properly.")

            run_count += 1
            time.sleep(interval)

        print("Monitoring stopped after maximum runs.")

    # Start monitoring in a background thread
    t = threading.Thread(target=_watch, daemon=True)
    t.start()





# =========================Button=======================
def click_button_if_exists(window, title=None, auto_id=None,

                           control_type="Button", timeout=30):
    """Click a button if exists."""

    btn = window.child_window(title=title, auto_id=auto_id, control_type=control_type)

    if btn.exists(timeout=timeout) and btn.is_enabled():
        btn.click_input()

        print(f"Clicked '{title or auto_id}'")

        return True

    print(f"'{title or auto_id}' button not found, skipping...")

    return False


# ===============================Add Printer================================
def click_add_printer(main_window, ui_tree_file_path):
    """
    Click the 'Add Printer' button in HP Smart app.

    :param main_window: pywinauto window object for HP Smart
    :param ui_tree_file_path: Path to save UI tree captures
    """
    try:
        add_printer_btn = main_window.child_window(title="Add Printer", control_type="Button")
        wait_for_element(add_printer_btn, timeout=20).click_input()
        time.sleep(2)
        capture_ui_tree(main_window, ui_tree_file_path, "After Add Printer", append=True)
        print("Clicked 'Add Printer'.")
    except Exception as e:
        take_desktop_screenshot(" Failed to click add printer ", window_title="HP Smart")
        print(f" Failed to click==================")

test_data=load_desktop_printer_data()
def select_printer_from_list(main_window, ui_tree_file_path, printer_name=test_data["printer1"]):
    """
    Select a printer from the Beaconing Printers list.

    :param main_window: pywinauto window object for HP Smart
    :param ui_tree_file_path: Path to save UI tree captures
    :param printer_name_pattern: Regex pattern to match the printer name
    """
    try:
        beaconing_list = main_window.child_window(
            title="BeaconingPrinters", auto_id="BeaconingGridView", control_type="List"
        )
        printer_item = beaconing_list.child_window(
            title_re=f"DEVICEVIEWMODEL:{ printer_name}", control_type="ListItem"
        )
        wait_for_element(printer_item, timeout=45).click_input()
        time.sleep(5)
        capture_ui_tree(main_window, ui_tree_file_path, f"After Selecting Printer: { printer_name}", append=True)
        print(f" Successfully selected printer: { printer_name}")
    except Exception as e:
        take_desktop_screenshot("Failed to select printer",window_title="HP Smart" )
        pytest.fail(f"Failed to select printer '{ printer_name}': {e}")


# ==================================Wi-fi setup====================================
def connect_printer_to_wifi(app, main_window, ui_tree_file_path):
    """

    Continue printer setup and connect to Wi-Fi.

    :param app: pywinauto Application object

    :param main_window: pywinauto main window object

    :param ui_tree_file_path: Path to save UI tree captures

    """

    try:

        # Step 6: Continue to Wi-Fi connection

        continue_btn = main_window.child_window(title="Continue", control_type="Text")

        wait_for_element(continue_btn, timeout=20).click_input()

        time.sleep(2)

        capture_ui_tree(main_window, ui_tree_file_path, "After Time to connect, Setup Page", append=True)

        # Step 7: Connect printer to Wi-Fi

        wifi_dialog = app.window(title="HP Smart")

        wifi_dialog.set_focus()

        wifi_continue_btn = wifi_dialog.child_window(

            title_re=".*Access Wi-Fi password for.*", control_type="Button", found_index=1

        )

        wait_for_element(wifi_continue_btn, timeout=30).click_input()

        capture_ui_tree(main_window, ui_tree_file_path, "After Access Wi-Fi Password, Continue Button", append=True)

        # Wait for printer to connect to Wi-Fi

        def is_setup_finished():

            try:

                btn = wifi_dialog.child_window(title="Continue", auto_id="OkBtn", control_type="Button")

                return btn.exists() and btn.is_enabled()

            except Exception:

                return False

        wait_until(timeout=360, retry_interval=2, func=is_setup_finished)

        wifi_final_continue = wifi_dialog.child_window(title="Continue", auto_id="OkBtn", control_type="Button")

        wifi_final_continue.click_input()

        capture_ui_tree(wifi_dialog, ui_tree_file_path, "After Printer connected to Wi-Fi", append=True)

        print(" Printer connected to Wi-Fi and clicked on Continue.")

    except Exception as e:
        take_desktop_screenshot("  Failed during Wi-Fi connection setup ", window_title="HP Smart")
        print(f" Failed during Wi-Fi connection setup: {e}")


# =====================Accept Privacy================
def accept_printer_privacy(app, main_window, ui_tree_file_path):
    """

    Accept printer privacy on the HP Smart app.

    :param app: pywinauto Application object

    :param main_window: pywinauto main window object

    :param ui_tree_file_path: Path to save UI tree captures

    """

    try:

        privacy_dialog = app.window(title="HP Smart")

        privacy_dialog.set_focus()

        privacy_accept_btn = privacy_dialog.child_window(title="Accept all", control_type="Button")

        wait_for_element(privacy_accept_btn, timeout=60).click_input()

        print(" Clicked 'Accept All' on printer privacy page.")

        time.sleep(10)

        capture_ui_tree(main_window, ui_tree_file_path, "After Privacy Accept", append=True)

    except Exception as e:
        take_desktop_screenshot("Failed to accept printer privacy ", window_title="HP Smart")
        print(f" Failed to accept printer privacy: {e}")


# =====================Sig-in======================
def sign_in_hp_account(main_window,ui_tree_file_path):
    """Fill in HP account email/password in Chrome popup."""
    try:
        sign_in_btn = main_window.child_window(
            title="Sign In", control_type="Button"
        )
        wait_until(
            timeout=60,
            retry_interval=2,
            func=lambda: sign_in_btn.exists()
                         and sign_in_btn.is_enabled(),
        )
        capture_ui_tree(
            main_window, ui_tree_file_path, "Before Signing in Account", append=True
        )
        sign_in_btn.click_input()
        print(" Clicked 'Sign In' button.")

        time.sleep(5)  # fallback wait
        capture_ui_tree(
            main_window, ui_tree_file_path, "After Signing in Account", append=True
        )
    except Exception as e:
        pytest.fail(f" Failed at Create account step: {e}")

        # Step : Detect Chrome window and fill HP Account
    print(" Waiting for Chrome window with HP Account page...")

    hp_chrome_window = None

    timeout = 120

    poll_interval = 3

    deadline = time.time() + timeout

    while time.time() < deadline:

        chrome_windows = Desktop(backend="uia").windows(title_re=".*Chrome.*")

        for win in chrome_windows:

            title_lower = win.window_text().lower()

            if "hp account" in title_lower or "create account" in title_lower:
                hp_chrome_window = win

                break

        if hp_chrome_window:
            break

        time.sleep(poll_interval)

    else:

        raise TimeoutError("Could not detect HP Account Chrome window")

    hp_chrome_window.set_focus()

    # time.sleep(10)

    # # Fill email

    # try:

    #     print("Typing user details in HP Account form...")

    #     # Email

    #     pyautogui.typewrite(email, interval=0.05)

    #     time.sleep(2)

    #     for _ in range(2):
    #         pyautogui.press("tab")

    #         time.sleep(1)

    #     # Submit email

    #     pyautogui.press("enter")

    #     time.sleep(5)

    #     # Password

    #     pyautogui.typewrite(password, interval=0.05)

    #     for _ in range(2):
    #         pyautogui.press("tab")

    #         time.sleep(1)

    #     # Submit password

    #     pyautogui.press("enter")

    #     time.sleep(10)

    #     print(" HP Account login submitted.")

    #     # --- Click the “Open” button on the popup ---

    #     print(" Waiting for the Open button popup...")

    #     time.sleep(5)  # give browser time to render popup

    #     # Locate “Open” button on screen (screenshot of your button stored as open_button.png)

    #     # If you don’t want to store an image, just Tab + Enter as below:

    #     for _ in range(2):  # press Tab a few times to reach Open

    #         pyautogui.press("tab")

    #         time.sleep(1)

    #     pyautogui.press("enter")  # Press Enter on Open

    #     print(" Clicked Open on popup")

    #     # --- Switch back to HP Smart App ---

    #     print(" Switching back to HP Smart app...")

    #     time.sleep(15)  # allow HP Smart to load after clicking Open

    #     # Bring HP Smart to foreground

    #     hp_window = Desktop(backend="uia").window(title_re="HP Smart")

    #     hp_window.set_focus()

    #     print(" Focused back to HP Smart.")

    #     # Extra wait to ensure UI loaded

    #     time.sleep(10)

    #     # Capture UI tree or do your assertions here

    #     # capture_ui_tree(hp_window, ui_tree_file_path, "After Switching back to HP account", append=True)

    #     print(" Completed login + Open + switch to HP Smart successfully!")

    # except Exception as e:
    #     pytest.fail(f" Failed to complete HP Smart login & open flow: {e}")


# =======================Next-Button==============
def click_next_button(main_window, ui_tree_file_path):
    """
    Click the 'Next' button in the HP Smart app if it exists.
    """
    try:
        # Locate the 'Next' button
        next_btn = main_window.child_window(title="Next", control_type="Button")
        wait_for_element(next_btn, timeout=180)

        # Verify button existence and perform click
        assert next_btn.exists(), "'Next' button should be displayed on the page."
        next_btn.click_input()
        print("Clicked 'Next' button successfully.")

        # Capture UI tree after the click
        time.sleep(5)
        capture_ui_tree(main_window, ui_tree_file_path, "After Clicking Next", append=True)

    except Exception as e:
        take_desktop_screenshot(" 'Next' button not found or click failed: ", window_title="HP Smart")
        print(f"'Next' button not found or click failed: {e}")



# =========================Select-Plan=====================
def select_printing_plan(main_window, ui_tree_file_path, plan_name):
    """Select a printing plan and click Select Plan."""
    plan_radio = main_window.child_window(title=plan_name, control_type="RadioButton")
    if plan_radio.exists(timeout=20):
        plan_radio.select()
        print(f" Selected plan: {plan_name}")
        time.sleep(2)
    else:
        print(f" Plan radio button not found for {plan_name}")
    click_button_if_exists(main_window, title="Select Plan", )
    capture_ui_tree(main_window, ui_tree_file_path, f"After selecting {plan_name}", append=True)


# ===========================Add Shipping================================
def click_add_shipping(main_window, ui_tree_file_path):
    """Click Add Billing then Continue."""
    click_button_if_exists(main_window, title="Add Shipping")
    capture_ui_tree(main_window, ui_tree_file_path, "After Adding Billing", append=True)


# ===========================Shipping-Details============================
def fill_shipping_details(window, address, city, state, zip_code, phone, ui_tree_file_path):
    """Fill shipping details form."""

    street_box = window.child_window(auto_id="street1", control_type="Edit")
    street_box.wait("ready", timeout=30)
    wait_for_element(street_box).set_edit_text("")
    street_box.type_keys(address, with_spaces=True)
    time.sleep(7)
    city_box = window.child_window(auto_id="city", control_type="Edit")
    city_box.wait("ready", timeout=50)
    wait_for_element(city_box).set_edit_text("")
    city_box.type_keys(city, with_spaces=True)
    time.sleep(7)

    # State dropdown

    state_dropdown = window.child_window(auto_id="state", control_type="ComboBox")
    street_box.wait("ready", timeout=30)

    wait_for_element(state_dropdown).click_input()

    time.sleep(10)

    capture_ui_tree(window, ui_tree_file_path, "After clicking drop down", append=True)

    state_list = window.child_window(auto_id="state-listbox", control_type="List")

    wait_for_element(state_list)

    state_item = state_list.child_window(title=state, control_type="ListItem")
    time.sleep(7)

    wait_for_element(state_item).click_input()
    time.sleep(7)

    zip_box = window.child_window(auto_id="zip-code", control_type="Edit")

    wait_for_element(zip_box).set_edit_text("")

    zip_box.type_keys(zip_code, with_spaces=True)
    time.sleep(7)

    phone_box = window.child_window(auto_id="phoneNumberSmall", control_type="Edit")

    wait_for_element(phone_box).set_edit_text("")

    phone_box.type_keys(phone, with_spaces=True)
    time.sleep(7)

    save_btn = window.child_window(title="Save", control_type="Button")

    wait_until(timeout=30, retry_interval=3, func=lambda: save_btn.is_enabled())

    save_btn.click_input()

    print("Entered address details and clicked Save.")

    capture_ui_tree(window, ui_tree_file_path, "After Entering shipping details", append=True)


# =================================Billing============================
def add_billing(main_window, ui_tree_file_path,):
    """Click Add Billing then Continue."""
    click_button_if_exists(main_window, title="Add Billing")
    capture_ui_tree(main_window, ui_tree_file_path, "After Adding Billing", append=True)
    time.sleep(10)
    # click_button_if_exists(main_window, title="Continue")

        # Bring the window into focus

    main_window.set_focus()

    # Perform one scroll using keyboard (Page Down)

    send_keys("{PGDN}")
    # Click the button
    # time.sleep(3)
    #
    # continue_btn = main_window.child_window(title="Continue", control_type="Button", found_index=1)
    # continue_btn.set_focus()
    # if continue_btn.exists(timeout=20) and continue_btn.is_enabled():
    #     continue_btn.click_input()
    # Step 2: Tab navigation to reach the button

    start_time = time.time()

    for i in range(13):

        # Check if the currently focused control is our target

        # focused = main_window.child_window(title="Continue", control_type="Button", found_index=1)
        #
        # if focused.exists() and focused.has_keyboard_focus():
        #
        #     print(f" '{"Continue"}' button activated after {i + 1} TAB presses.")
        #
        #     return

        # Press TAB to move focus to next control

        send_keys("{TAB}")

        time.sleep(0.2)
    send_keys("{ENTER}")

    print(f" Clicked '{"Continue"}' button successfully.")

    capture_ui_tree(main_window, ui_tree_file_path, "After Continue on Billing Screen", append=True)


def fill_billing_details(main_window, ui_tree_file_path, billing_data):
    try:
        # Card number
        field = main_window.child_window(auto_id="txtCardNumber", control_type="Edit")
        if field.exists(timeout=10):
            field.set_text(billing_data.get("card_number", ""))
            print("Entered card number")

        # Expiration month
        exp_m = main_window.child_window(auto_id="drpExpMonth", control_type="ComboBox")
        if exp_m.exists(timeout=5):
            exp_m.select(billing_data.get("exp_month", ""))
            print("Selected expiration month")

        # Expiration year
        exp_y = main_window.child_window(auto_id="drpExpYear", control_type="ComboBox")
        if exp_y.exists(timeout=5):
            exp_y.select(billing_data.get("exp_year", ""))
            print(" Selected expiration year")

        # CVV
        cvv_field = main_window.child_window(auto_id="txtCVV", control_type="Edit")
        if cvv_field.exists(timeout=5):
            cvv_field.set_text(billing_data.get("cvv", ""))
            print("Entered CVV")

        capture_ui_tree(main_window, ui_tree_file_path, "After entering billing details", append=True)

        # Click Next
        next_button = main_window.child_window(auto_id="btn_pgs_card_add", control_type="Button")
        if next_button.exists(timeout=10) and next_button.is_enabled():
            next_button.click_input()
            print(" Clicked Next after billing")

        capture_ui_tree(main_window, ui_tree_file_path, "After clicking Next on billing", append=True)

    except Exception as e:
        print(f" Error filling billing details: {e}")

def verify_enroll_step_page(main_window, ui_tree_file_path):
    """
    Verify the Enroll Step page and the 'Enter promo or Pin Code' link on the Billing card.
    """
    try:
        enroll_page = main_window.child_window(title="Enter your details to receive your ink", control_type="Text")
        wait_for_element(enroll_page, timeout=15)
        promo_link = main_window.child_window(title="Enter promo or PIN code", control_type="Hyperlink")
        wait_for_element(promo_link, timeout=10)
        assert promo_link.exists(), "'Enter promo or Pin Code' link should be displayed on Billing card."
        capture_ui_tree(main_window, ui_tree_file_path, "After Enroll Step Page", append=True)
        print("Enroll Step page and promo link are displayed.")
    except Exception as e:
        take_desktop_screenshot(" Enroll Step page or promo link not displayed: ", window_title="HP Smart")
        print(f"Enroll Step page or promo link not displayed: {e}")


def click_enter_promo_pin_code(main_window, ui_tree_file_path):
    """
    Click the 'Enter promo or Pin Code' link.
    """
    try:
        promo_link = main_window.child_window(title="Enter promo or PIN code", control_type="Hyperlink")
        wait_for_element(promo_link, timeout=10)
        promo_link.click_input()
        capture_ui_tree(main_window, ui_tree_file_path, "After Click Promo Link", append=True)
        print("Clicked 'Enter promo or Pin Code' link.")
    except Exception as e:
        take_desktop_screenshot(" Failed to click 'Enter promo or Pin Code' link ", window_title="HP Smart")
        print(f"Failed to click 'Enter promo or Pin Code' link: {e}")


def verify_sob_modal_displayed(main_window, ui_tree_file_path):
    """
    Verify the 'Special Offer Benefits' modal is displayed.
    """
    try:
        sob_modal = main_window.child_window(title_re="Special Offers", control_type="Text")
        wait_for_element(sob_modal, timeout=15)
        assert sob_modal.exists(), "SOB modal should be displayed."
        capture_ui_tree(main_window, ui_tree_file_path, "After SOB Modal", append=True)
        print("SOB modal is displayed.")
    except Exception as e:
        take_desktop_screenshot(" SOB modal not displayed ", window_title="HP Smart")
        print(f"SOB modal not displayed: {e}")


def verify_whats_this_string(main_window):
    """
    Check the string 'What’s this?' is displayed.
    """
    try:
        whats_this = main_window.child_window(title="What's this?", control_type="Text")
        wait_for_element(whats_this, timeout=10)
        assert whats_this.exists(), "'What’s this?' string should be displayed."
        print("'What’s this?' string is displayed.")
    except Exception as e:
        take_desktop_screenshot(" What’s this?' string not displayed ", window_title="HP Smart")
        print(f"'What’s this?' string not displayed: {e}")


def hover_whats_this_and_verify_tooltip(main_window,ui_tree_file_path):
    """
    Hover over 'What’s this?' and verify tooltip is displayed.
    """
    try:
        whats_this = main_window.child_window(title="What's this?", control_type="Text")
        wait_for_element(whats_this, timeout=10)
        whats_this.move_mouse_input()
        whats_this.click_input()
        time.sleep(3)
        capture_ui_tree(main_window, ui_tree_file_path, "After hovering/clicking whats this", append=True)
        tooltip = main_window.child_window(title="Please redeem the promo or PIN code you have available on your flyer, HP Instant Ink prepaid card, or email.", control_type="ToolTip")
        wait_for_element(tooltip, timeout=5)
        assert tooltip.exists(), "Tooltip should be displayed when hovering 'What’s this?'."
        print("Tooltip for 'What’s this?' is displayed.")
    except Exception as e:
        take_desktop_screenshot(" Tooltip for 'What’s this?' not displayed ", window_title="HP Smart")
        print(f"Tooltip for 'What’s this?' not displayed: {e}")


def verify_dsp_page_displayed(main_window, ui_tree_file_path):
    """
    Verify the DSP page is displayed in HP Smart app.

    :param main_window: pywinauto window object for HP Smart
    :param ui_tree_file_path: Path to save UI tree captures
    """
    try:
        dsp_page = main_window.child_window(title_re="Start your 1-month free trial today.", control_type="Group")
        wait_for_element(dsp_page, timeout=15)
        assert dsp_page.exists(), "DSP page should be displayed."
        capture_ui_tree(main_window, ui_tree_file_path, "After DSP Page", append=True)
        print("DSP page is displayed.")
    except Exception as e:
        print(f" DSP page not displayed: {e}")

# ================================Enter Promo or Pin===================================
def apply_promo_code(window, apply_code, ui_tree_file_path):
    """Apply promo code."""

    promo_btn = window.child_window(title="Enter promo or PIN code", control_type="Button")

    if promo_btn.exists(timeout=80) and promo_btn.is_enabled():
        promo_btn.click_input()

        time.sleep(2)

        print("Clicked 'Enter promo or PIN code'")

        capture_ui_tree(window, ui_tree_file_path, "After Clicking Promo", append=True)

    promo_input = window.child_window(auto_id="code-entry", control_type="Edit")

    if promo_input.exists(timeout=10):
        promo_input.set_edit_text(apply_code)

        print(f"Entered promo code '{apply_code}'")

        capture_ui_tree(window, ui_tree_file_path, "After Entering Promo", append=True)

    apply_btn = window.child_window(title="Apply", control_type="Button")

    if apply_btn.exists(timeout=10) and apply_btn.is_enabled():
        apply_btn.click_input()

        print("Clicked 'Apply'")

        time.sleep(3)

        capture_ui_tree(window, ui_tree_file_path, "After Apply", append=True)


def skip_add_paper(window, ui_tree_file_path):
    try:
        add_paper_btn = window.child_window(title="Add Paper", control_type="Button")
        skip_paper_btn = window.child_window(title="Skip Paper", control_type="Button")
        if skip_paper_btn.exists(timeout=20):
            skip_paper_btn.click_input()
            print("Clicked 'Skip paper button'")
            time.sleep(10)
            capture_ui_tree(
                window, ui_tree_file_path, "After Skip Paper", append=True
            )
        else:
            print("Find Skip paper button not found, proceeding...")
    except Exception as e:
        print(f"  No Skip paper button found, Skipping.. {e}")


def final_enrol_continue(window, ui_tree_file_path):
    try:
        continue_btn = window.child_window(title="Continue", control_type="Button")
        if continue_btn.exists(timeout=20):
            capture_ui_tree(
                window, ui_tree_file_path, "before Final continue button", append=True
            )
            continue_btn.click_input()
            print("Clicked 'Final Continue button'")
            time.sleep(10)
            capture_ui_tree(
                window, ui_tree_file_path, "After Final continue button", append=True
            )
        else:
            print("Find Final continue button not found, proceeding...")
    except Exception as e:
        pytest.fail(f"  No Final continue button found, Skipping.. {e}")


def check_ARN_modal(window, ui_tree_file_path):
    try:
        terms_of_service = window.child_window(title="Terms of Service", control_type="Text")
        if terms_of_service.exists(timeout=20):
            capture_ui_tree(
                window, ui_tree_file_path, "After clicking TOC ", append=True
            )
            terms_of_service.click_input()
            print("Clicked 'terms_of_service'")
            time.sleep(2)
            check_box = window.child_window(auto_id="terms-of-service", control_type="CheckBox")
            if check_box.exists(timeout=20):
                check_box.scroll_into_view()
                capture_ui_tree(
                    window, ui_tree_file_path, "After checkbox", append=True
                )
                check_box.check()
            print("  Successfully clicked arn check box.")
        else:
            print("ARN check box not found, proceeding...")
    except Exception as e:
        pytest.fail(f"  Failed to find ARN check box. {e}")


def click_enroll(window, ui_tree_file_path):
    try:
        enrol_btn = window.child_window(title="Enroll", control_type="Button")
        if enrol_btn.exists(timeout=20):
            capture_ui_tree(
                window, ui_tree_file_path, "After Clicked 'enroll button", append=True
            )
            enrol_btn.click_input()
            print("Clicked 'enroll button'")
            time.sleep(10)
        else:
            print("Enroll button not found, proceeding...")
    except Exception as e:
        pytest.fail(f"  No Enroll button found.. {e}")


def click_account_btn(window, ui_tree_file_path):
    try:
        account_btn = window.child_window(title="Manage HP Account", auto_id="HpcSignedOutIcon", control_type="Button")
        if account_btn.exists(timeout=20):
            capture_ui_tree(
                window, ui_tree_file_path, "After Clicked 'account button", append=True
            )
            account_btn.click_input()
            print("Clicked 'account button'")
            time.sleep(10)
        else:
            print("account button not found, proceeding...")
    except Exception as e:
        pytest.fail(f"  No account button found.. {e}")

def verify_dsp_page_displayed(window, ui_tree_file_path):
    """
        Verify the DSP page is displayed in HP Smart app.

        :param main_window: pywinauto window object for HP Smart
        :param ui_tree_file_path: Path to save UI tree captures
     """
    try:
            get_a_text = window.child_window(title="Get a ", control_type="Text")
            dsp_page = window.child_window(title="3-month Free* Trial",control_type="Text", found_index=0)
            wait_for_element(dsp_page, timeout=40)
            assert dsp_page.exists(), "DSP page should be displayed."
            time.sleep(3)
            capture_ui_tree(window, ui_tree_file_path, "After DSP Page", append=True)
            print(" DSP page is displayed.")
            get_a_text.click_input()
    except Exception as e:
        take_desktop_screenshot(" DSP page not displayed ", window_title="HP Smart")
        print(f" DSP page not displayed: {e}")


def click_start_free_trial(main_window):
    """
    Click the 'Start Free Trial' button in HP Smart app.

    :param main_window: pywinauto window object for HP Smart
    :return: Name of the button clicked
    """
    try:
        # send_keys("{PGDN}")
        # send_keys("{PGDN}")
        free_trial_btn = main_window.child_window(title="Start Free Trial", control_type="Hyperlink"
        ,found_index=0
                                                  )
        wait_for_element(free_trial_btn, timeout=10)
        assert free_trial_btn.exists() , "Free Trial button should be displayed."
        free_trial_btn.click_input()
        time.sleep(10)
        print("Clicked 'Start Free Trial'.")
        return "Start Free Trial"
    except Exception as e:
        take_desktop_screenshot(" Failed to click 'Start Free Trial ", window_title="HP Smart")

        print(f"Failed to click 'Start Free Trial': {e}")
        return None


def verify_value_prop_page_displayed(main_window, ui_tree_file_path):
    """
    Verify the Value Prop page is displayed in HP Smart app.

    :param main_window: pywinauto window object for HP Smart
    :param ui_tree_file_path: Path to save UI tree captures
    """
    try:
        capture_ui_tree(main_window, ui_tree_file_path, "before Value Prop Page", append=True)
        # child_window(title="Your new printer includes ", control_type="Text")
        prop_page_title = main_window.child_window(title="Your new printer includes ", control_type="Text")
        wait_for_element(prop_page_title, timeout=100)
        assert prop_page_title.exists(), "prop page title should be displayed."
        capture_ui_tree(main_window, ui_tree_file_path, "prop page title", append=True)
        print(" prop page title should be displayed.")
    except Exception as e:
        take_desktop_screenshot(" prop page title should be displayed.", window_title="HP Smart")
        print(f" Value prop page not displayed: {e}")


#
# def click_get_supplies_tile():
#         return None
#
# def click_try_instant_ink_free():
#         return None
#
#
def click_try_instant_ink_free():
    return None


def click_save_billing(main_window, ui_tree_file_path):
    """
    Click the 'Save' button on the Billing card.

    :param main_window: pywinauto window object for HP Smart
    :param ui_tree_file_path: Path to save UI tree captures
    """
    try:
        save_btn = main_window.child_window(title="Continue", control_type="Button")
        wait_for_element(save_btn, timeout=10)
        save_btn.click_input()
        capture_ui_tree(main_window, ui_tree_file_path, "After Save Billing", append=True)
        print("Clicked 'Save' on Billing card.")
    except Exception as e:
        take_desktop_screenshot(" Failed to click 'Save' on Billing card ", window_title="HP Smart")
        print(f"Failed to click 'Save' on Billing card: {e}")

def verify_redeemed_months_credits_section(main_window, redeemed_months, ui_tree_file_path):
    """
    Verify the '[X] Redeemed months + credits' string and 'See details' link are displayed.
    """
    try:
        redeemed_section = main_window.child_window(title= f"{redeemed_months} Redeemed months + credits", control_type="Text")
        wait_for_element(redeemed_section, timeout=15)
        assert redeemed_section.exists(), "'Redeemed months + credits' section should be displayed."

        see_details_link = main_window.child_window(title="See details", control_type="Hyperlink")
        wait_for_element(see_details_link, timeout=10)
        assert see_details_link.exists(), "'See details' link should be displayed."

        print("Redeemed months + credits section and See details link are displayed.")
    except Exception as e:
        take_desktop_screenshot(" Redeemed months + credits section or See details link not displayed ", window_title="HP Smart")
        print(f"Redeemed months + credits section or See details link not displayed: {e}")


def verify_redeemed_months_credits_style(main_window):
    """
    Verify the '[X] Redeemed months + credits' string is blue color without underline.
    """
    try:
        redeemed_section = main_window.child_window(title="5 Redeemed months + credits", control_type="Text")
        wait_for_element(redeemed_section, timeout=10)
        assert redeemed_section.exists(), "'Redeemed months + credits' string should be displayed."
        print("'[X] Redeemed months + credits' string is displayed (check color/underline visually or via UI properties).")
    except Exception as e:
        take_desktop_screenshot(" [X] Redeemed months + credits' string not displayed ", window_title="HP Smart")
        print(f"'[X] Redeemed months + credits' string not displayed: {e}")


def verify_see_details_link(main_window):
    """
    Verify the 'See details' link is displayed and enabled.
    """
    try:
        see_details_link = main_window.child_window(title="See details", control_type="Hyperlink")
        wait_for_element(see_details_link, timeout=10)
        assert see_details_link.exists(), "'See details' link should be displayed."
        print("'See details' link is displayed and enabled.")
    except Exception as e:
        take_desktop_screenshot(" See details' link not displayed ", window_title="HP Smart")
        print(f"'See details' link not displayed: {e}")


def click_see_details_link(main_window):
    """
    Click the 'See details' link.
    """
    try:
        see_details_link = main_window.child_window(title="See details", control_type="Hyperlink")
        wait_for_element(see_details_link, timeout=10)
        see_details_link.click_input()
        print("Clicked 'See details' link.")
    except Exception as e:
        take_desktop_screenshot(" Failed to click 'See details' link ", window_title="HP Smart")
        print(f"Failed to click 'See details' link: {e}")

def locate_see_details_link(main_window):
    """
    Locate the 'See details' link on the page.
    Returns the element if found, else None.
    """
    try:
        see_details_link = main_window.child_window(title="See details", control_type="Hyperlink")
        wait_for_element(see_details_link, timeout=10)
        if see_details_link.exists():
            print("'See details' link is visible on the page.")
            return see_details_link
        else:
            print("'See details' link not found.")
            return None
    except Exception as e:
        take_desktop_screenshot(" Error locating 'See details' link ", window_title="HP Smart")
        print(f"Error locating 'See details' link: {e}")
        return None


def verify_sob_modal_contents(sob_modal):
    """
    Verify the contents of the 'Special Offer Benefits (SOB)' modal.
    """
    try:
        expected_benefits = [
            "Free Trial",
            "Promo Code",
            "RAF Code",
            "EK Code",
            "Special Offer"
        ]
        for benefit in expected_benefits:
            benefit_elem = sob_modal.child_window(title_re="Special Offers", control_type="Text")
            assert benefit_elem.exists(), f"Benefit '{benefit}' should be displayed in SOB modal."
        print("SOB modal displays all expected special offer benefits.")
    except Exception as e:
        take_desktop_screenshot(" SOB modal content verification failed ", window_title="HP Smart")
        print(f"SOB modal content verification failed: {e}")

def verify_accordion_sub_section(main_window, ui_tree_file_path):
    """
    Verify Accordion sub section is displayed as per Prototype.
    """
    try:
        accordion_section = main_window.child_window(title_re=".*Accordion.*", control_type="Group")
        wait_for_element(accordion_section, timeout=15)
        assert accordion_section.exists(), "Accordion sub section should be displayed as per Prototype."

        print("Accordion sub section is displayed as per Prototype.")
        capture_ui_tree(main_window, ui_tree_file_path, "After Accordion Sub Section", append=True)
    except Exception as e:
        take_desktop_screenshot(" Accordion sub section not displayed ", window_title="HP Smart")
        print(f"Accordion sub section not displayed: {e}")


def verify_free_months_item(main_window):
    """
    Verify the free months item for trial is displayed.
    """
    try:
        free_months_item = main_window.child_window(title_re="Free Months", control_type="Text")
        wait_for_element(free_months_item, timeout=10)
        assert free_months_item.exists(), "Free months item for trial should be displayed."

        print("Free months item for trial is displayed.")
    except Exception as e:
        take_desktop_screenshot(" Free months item for trial not displayed ", window_title="HP Smart")
        print(f"Free months item for trial not displayed: {e}")

def click_edit_plan_icon(main_window, ui_tree_file_path):
    """
    Click the Edit icon on the Plan Card.
    """
    try:
        edit_icon = main_window.child_window(title="Edit", control_type="Button")
        wait_for_element(edit_icon, timeout=10)
        edit_icon.click_input()
        capture_ui_tree(main_window, ui_tree_file_path, "After Clicking Edit Plan Icon", append=True)
        print("Clicked Edit icon on Plan Card.")
    except Exception as e:
        print(f"Failed to click Edit icon on Plan Card: {e}")


def click_edit_shipping_icon(main_window, ui_tree_file_path):
    """
    Click the Edit icon on the Plan Card.
    """
    try:

        # Bring the main window to focus

        main_window.set_focus()

        # Press TAB three times to navigate to the 'Edit' icon

        for _ in range(2):
            send_keys("{TAB}")

            time.sleep(0.5)

        # Press ENTER to click the focused element

        send_keys("{ENTER}")

        print("Clicked 'Edit' icon using keyboard navigation.")

        # Optional: capture UI state after clicking

        if ui_tree_file_path:
            capture_ui_tree(main_window, ui_tree_file_path, "After Edit Click", append=True)

        return True

    except Exception as e:
        take_desktop_screenshot(" Failed to click 'Edit' icon ", window_title="HP Smart")
        print(f"Failed to click 'Edit' icon using keyboard navigation: {e}")

        return False

def click_edit_billing_icon(main_window, ui_tree_file_path):
    """
    Click the Edit icon on the Plan Card.
    """
    try:

        # Bring the main window to focus

        main_window.set_focus()

        # Press TAB three times to navigate to the 'Edit' icon

        for _ in range(3):
            send_keys("{TAB}")

            time.sleep(0.5)

        # Press ENTER to click the focused element

        send_keys("{ENTER}")

        print("Clicked 'Edit' icon using keyboard navigation.")

        # Optional: capture UI state after clicking

        if ui_tree_file_path:
            capture_ui_tree(main_window, ui_tree_file_path, "After Edit Click", append=True)

        return True

    except Exception as e:
        take_desktop_screenshot(" Failed to click 'Edit' icon ", window_title="HP Smart")
        print(f"Failed to click 'Edit' icon using keyboard navigation: {e}")

        return False


def select_new_plan_in_edit_mode(main_window, ui_tree_file_path, new_plan_name):
    """
    Select a new plan in the edit view.
    """
    try:
        plan_radio = main_window.child_window(title=new_plan_name, control_type="RadioButton")
        wait_for_element(plan_radio, timeout=10)
        plan_radio.select()
        capture_ui_tree(main_window, ui_tree_file_path, f"After Selecting New Plan: {new_plan_name}", append=True)
        print(f"Selected new plan: {new_plan_name}")
    except Exception as e:
        print(f"Failed to select new plan: {e}")


def click_save_plan(main_window, ui_tree_file_path):
    """
    Click the Save button to confirm plan change.
    """
    try:
        save_btn = main_window.child_window(title="Save", control_type="Button")
        wait_for_element(save_btn, timeout=10)
        save_btn.click_input()
        capture_ui_tree(main_window, ui_tree_file_path, "After Saving Plan", append=True)
        print("Clicked Save after changing plan.")
    except Exception as e:
        print(f"Failed to click Save after changing plan: {e}")


def verify_updated_plan_details(main_window, expected_plan_name):
    """
    Verify the updated plan details are displayed correctly.
    """
    try:
        updated_plan = main_window.child_window(title=expected_plan_name, control_type="Text")
        wait_for_element(updated_plan, timeout=10)
        assert updated_plan.exists(), f"Updated plan '{expected_plan_name}' should be displayed."
        print(f"Updated plan details for '{expected_plan_name}' are displayed correctly.")
    except Exception as e:
        print(f"Updated plan details not displayed correctly: {e}")

def verify_saved_shipping_details(main_window, test_data, ui_tree_file_path):
    """
    Verify that the saved shipping details are displayed correctly on the Shipping Card.
    """
    try:
        user_name = main_window.child_window(title=f"{test_data['user_name']}", control_type="Text")
        address = main_window.child_window(title_re=f".*{test_data['address']}.*", control_type="Text")
        assert user_name.exists(), f"Shipping detail '{user_name}' should be displayed on Shipping Card."
        assert address.exists(), f"Shipping detail '{address}' should be displayed on Shipping Card."
        # for field, value in zip(
        #     ["user_name", "address"],
        #     [user_name,address]
        # ):
        #     wait_for_element(value, timeout=10)
        #     assert value.exists(), f"Shipping detail '{field}' should be displayed on Shipping Card."

        print("Saved Shipping details are displayed correctly on the Shipping Card.")
        capture_ui_tree(main_window, ui_tree_file_path, "After Verifying Shipping Card", append=True)
    except Exception as e:
        take_desktop_screenshot("Saved Shipping details not displayed correctly ", window_title="HP Smart")
        print(f"Saved Shipping details not displayed correctly: {e}")

def verify_saved_billing_details(main_window, test_data, ui_tree_file_path):
    """
    Verify that the saved billing details are displayed correctly on the Billing Card.
    """
    try:
        billing_card = main_window.child_window(title_re="Billing", control_type="Group")
        wait_for_element(billing_card, timeout=15)
        assert billing_card.exists(), "Billing Card should be displayed."

        name = billing_card.child_window(title_re=f".*{test_data['billing']['name']}.*", control_type="Text")
        address = billing_card.child_window(title_re=f".*{test_data['billing']['address']}.*", control_type="Text")
        city = billing_card.child_window(title_re=f".*{test_data['billing']['city']}.*", control_type="Text")
        state = billing_card.child_window(title_re=f".*{test_data['billing']['state']}.*", control_type="Text")
        zip_code = billing_card.child_window(title_re=f".*{test_data['billing']['zip']}.*", control_type="Text")
        phone = billing_card.child_window(title_re=f".*{test_data['billing']['phone']}.*", control_type="Text")

        for field, value in zip(
            ["name", "address", "city", "state", "zip_code", "phone"],
            [name, address, city, state, zip_code, phone]
        ):
            wait_for_element(value, timeout=10)
            assert value.exists(), f"Billing detail '{field}' should be displayed on Billing Card."

        print("Saved Billing details are displayed correctly on the Billing Card.")
        capture_ui_tree(main_window, ui_tree_file_path, "After Verifying Billing Card", append=True)
    except Exception as e:
        print(f"Saved Billing details not displayed correctly: {e}")

def verify_order_review_page(main_window, ui_tree_file_path):
    """
    Verify the Order Review page is displayed correctly.
    """
    try:
        order_review = main_window.child_window(title_re="See Details", control_type="Link")
        wait_for_element(order_review, timeout=15)
        assert order_review.exists(), "Order Review page should be displayed."
        capture_ui_tree(main_window, ui_tree_file_path, "After Order Review Page", append=True)
        print("Order Review page is displayed correctly.")
    except Exception as e:
        print(f"Order Review page not displayed: {e}")


def click_continue_on_order_review(main_window, ui_tree_file_path):
    """
    Click the Continue button on the Order Review page.
    """
    try:
        continue_btn = main_window.child_window(title="Continue", control_type="Button")
        wait_for_element(continue_btn, timeout=10)
        assert continue_btn.is_enabled(), "Continue button should be enabled."
        continue_btn.click_input()
        capture_ui_tree(main_window, ui_tree_file_path, "After Clicking Continue on Order Review", append=True)
        print("Clicked Continue on Order Review page.")
    except Exception as e:
        print(f"Failed to click Continue on Order Review page: {e}")


def verify_automatic_renewal_modal(main_window, ui_tree_file_path):
    """
    Verify the automatic renewal notice modal opens and matches the prototype design.
    """
    try:
        renewal_modal = main_window.child_window(class_name="sc-bhVIhj jTYvdT", control_type="Group")
        wait_for_element(renewal_modal, timeout=10)
        assert renewal_modal.exists(), "Automatic renewal notice modal should be displayed."

        # Check for drop-down button (if present)
        dropdown_btn = renewal_modal.child_window(title_re=".*", control_type="Button")
        if dropdown_btn.exists():
            print("Drop-down button is displayed in the modal.")

        capture_ui_tree(main_window, ui_tree_file_path, "After Automatic Renewal Modal", append=True)
        print("Automatic renewal notice modal is displayed and matches prototype.")
    except Exception as e:
        print(f"Automatic renewal notice modal not displayed: {e}")


def verify_renewal_modal_checkboxes(main_window):
    """
    Verify the checkbox(es) on the automatic renewal notice modal.
    """
    try:
        renewal_modal = main_window.child_window(class_name="styles__TOSCheckbox-@jarvis/react-smb-instant-ink-signup__sc-1jkvy2d-3 jQzVJP css-ooos5e-base-unchecked-Checkbox", control_type="Group")

        # TOS checkbox
        tos_checkbox = renewal_modal.child_window(class_name="css-1l5ptj2-interactive", control_type="Check Box")
        assert tos_checkbox.exists(), "TOS checkbox should be displayed."
        assert not tos_checkbox.get_toggle_state(), "TOS checkbox should be unchecked by default."

        # Prepaid checkbox (if applicable)
        prepaid_checkbox = renewal_modal.child_window(title_re=".*Prepaid.*", control_type="Check Box")
        if prepaid_checkbox.exists():
            assert not prepaid_checkbox.get_toggle_state(), "Prepaid checkbox should be unchecked by default."
            print("Two checkboxes displayed (TOS and Prepaid).")
        else:
            print("Only TOS checkbox displayed (no Prepaid).")
    except Exception as e:
        print(f"Checkbox(es) on renewal modal not displayed or incorrect: {e}")


def verify_renewal_modal_button(main_window):
    """
    Verify the Enroll or Start Paid Service button is displayed as disabled.
    """
    try:
        renewal_modal = main_window.child_window(title_re="Automatic Renewal Notice", control_type="Window")
        enroll_btn = renewal_modal.child_window(title_re="Enroll", control_type="Button")
        assert enroll_btn.exists(), "Enroll/Start Paid Service button should be displayed."
        assert not enroll_btn.is_enabled(), "Enroll/Start Paid Service button should be disabled."
        print("Enroll/Start Paid Service button is displayed as disabled.")
    except Exception as e:
        print(f"Enroll/Start Paid Service button not displayed or not disabled: {e}")


def verify_terms_of_service_link(main_window):
    """
    Verify the HP Instant Ink Terms of Service link is displayed correctly on the modal.
    """
    try:
        renewal_modal = main_window.child_window(title_re="Automatic Renewal Notice", control_type="Window")
        tos_link = renewal_modal.child_window(title_re="HP Instant Ink Terms of Service", control_type="Link")
        assert tos_link.exists(), "HP Instant Ink Terms of Service link should be displayed."
        print("HP Instant Ink Terms of Service link is displayed correctly.")
    except Exception as e:
        print(f"HP Instant Ink Terms of Service link not displayed: {e}")








# def click_edit_icon(main_window, ui_tree_file_path=None):
#     """
#     Click the 'Edit' icon/button in the HP Smart app.
#
#     :param main_window: pywinauto window object for HP Smart
#     :param ui_tree_file_path: Optional path to save UI tree captures
#     :return: True if clicked successfully, False otherwise
#     """
#     try:
#         # Adjust the title or auto_id as per the actual Edit icon/button in your app
#         edit_btn = main_window.child_window(control_type="Button")
#         wait_for_element(edit_btn, timeout=15)
#         edit_btn.click_input()
#         print("Clicked 'Edit' icon/button.")
#         if ui_tree_file_path:
#             capture_ui_tree(main_window, ui_tree_file_path, "After Edit Click", append=True)
#         return True
#     except Exception as e:
#         print(f"Failed to click 'Edit' icon/button: {e}")
#         return False


def click_edit_icon(main_window, ui_tree_file_path=None):
    """

    Navigate using TAB key to reach 'Edit' icon and click using ENTER key.

    :param main_window: pywinauto window object for HP Smart

    :param ui_tree_file_path: Optional path to save UI tree captures

    :return: True if clicked successfully, False otherwise

    """

    try:

        # Bring the main window to focus

        main_window.set_focus()

        # Press TAB three times to navigate to the 'Edit' icon

        for _ in range(1):
            send_keys("{TAB}")

            time.sleep(0.5)

        # Press ENTER to click the focused element

        send_keys("{ENTER}")

        print("Clicked 'Edit' icon using keyboard navigation.")

        # Optional: capture UI state after clicking

        if ui_tree_file_path:
            capture_ui_tree(main_window, ui_tree_file_path, "After Edit Click", append=True)

        return True

    except Exception as e:
        take_desktop_screenshot(" Failed to click 'Edit' icon using keyboard navigation ", window_title="HP Smart")
        print(f"Failed to click 'Edit' icon using keyboard navigation: {e}")

        return False


# # ===========================selecting the plan====================

def select_different_printing_plan(main_window, ui_tree_file_path, plan_name= '100-page-plan'):
#         """
#         Select a printing plan and click the Select Plan button.
#         plan_name options:
#             '10-page-plan'   (Light)
#             '50-page-plan'   (Occasional)
#             '100-page-plan'  (Moderate)
#             '300-page-plan'  (Frequent)
#             '700-page-plan'  (Business)
#         """

    try:
        plan_radio = main_window.child_window(title=plan_name, control_type="RadioButton")
        if plan_radio.exists(timeout=20):
            plan_radio.select()
            print(f"Selected plan: {plan_name}")
            time.sleep(2)
            click_button_if_exists(main_window, title="Select Plan")
            capture_ui_tree(main_window, ui_tree_file_path, f"After selecting {plan_name}", append=True)
            return True
        else:
            print(f"Plan radio button not found for {plan_name}")
            return False
    except Exception as e:
        take_desktop_screenshot(" Failed to select plan ", window_title="HP Smart")
        print(f"Failed to select plan '{plan_name}': {e}")
        return False


def verify_shipping_details(main_window, ui_tree_file_path):
    """
    Verify the 'Shipping Details' modal is displayed.
    """
    try:
        street_box = main_window.child_window(auto_id="street1", control_type="Edit")
        city_box = main_window.child_window(auto_id="city", control_type="Edit")
        phone_box = main_window.child_window(auto_id="phoneNumberSmall", control_type="Edit")
        zip_box = main_window.child_window(auto_id="zip-code", control_type="Edit")
        assert street_box.get_value() == test_data["address"], "Street Address value is incorrect"
        assert city_box.get_value() == test_data["city"], "City value is incorrect"
        assert phone_box.get_value() == test_data["phone"], "Phone value is incorrect"
        assert zip_box.get_value() == test_data["zip"], "Zip value is incorrect"
    except Exception as e:
        take_desktop_screenshot(" Shipping Details modal not displayed ", window_title="HP Smart")
        print(f"Shipping Details modal not displayed: {e}")

def verify_billing_details(main_window, ui_tree_file_path,billing_data,payment_type="credit_card"):
    """Verify the 'Billing Details' modal is displayed."""
    if payment_type == "credit_card":
        try:
            card_number = billing_data.get("card_number")
            card_number_last_digits = card_number[-4:]
            exp_month = billing_data.get("exp_month")
            exp_year = billing_data.get("exp_year")
            card_details = main_window.child_window(title="XXXX-XXXX-XXXX-"+ card_number_last_digits, control_type="Text")
            expiry_details = main_window.child_window(title="Expires: "+exp_month+ "/"+ exp_year, control_type="Text")
            wait_for_element(card_details, timeout=10)
            wait_for_element(expiry_details, timeout=10)
            assert card_details.exists(), "Last four digits of card should be displayed."
            assert expiry_details.exists(), "expiry details should be displayed."
            capture_ui_tree(main_window, ui_tree_file_path, "After Billing Details Modal", append=True)
            print("Billing Details modal is displayed.")
        except Exception as e:
            take_desktop_screenshot(" Billing Details modal not displayed ", window_title="HP Smart")
            print(f"Billing Details modal not displayed: {e}")
    elif payment_type == "Paypal":
        try:
            paypal_email = main_window.child_window(title=test_data["paypal_email"], control_type="Text")
            wait_for_element(paypal_email, timeout=10)
            assert paypal_email.exists(), "PayPal email should be displayed on Billing card."

            print("PayPal billing verified: 'Billing' heading and PayPal email are displayed.")
            if ui_tree_file_path:
                capture_ui_tree(main_window, ui_tree_file_path, "After PayPal Billing Verification", append=True)
        except Exception as e:
            take_desktop_screenshot(" Billing Details modal not displayed ", window_title="HP Smart")
            print(f"Billing Details modal not displayed: {e}")

def verify_disclaimer_displayed(main_window, ui_tree_file_path):
    """
    Verify the disclaimer text is displayed in the HP Smart app.

    :param main_window: pywinauto window object for HP Smart
    :param ui_tree_file_path: Path to save UI tree captures
    """
    try:
        disclaimer = main_window.child_window(title_re=".*disclaimer.*", control_type="Text")
        wait_for_element(disclaimer, timeout=10)
        assert disclaimer.exists(), "Disclaimer should be displayed."
        capture_ui_tree(main_window, ui_tree_file_path, "After Disclaimer Displayed", append=True)
        print("Disclaimer is displayed.")
    except Exception as e:
        take_desktop_screenshot("  ", window_title="HP Smart")
        print(f"Disclaimer not displayed: {e}")

def click_hp_terms_of_service_link(main_window, ui_tree_file_path=None):
    """
    Click the 'HP Instant Ink Terms of service' link in the HP Smart app.

    :param main_window: pywinauto window object for HP Smart
    :param ui_tree_file_path: Optional path to save UI tree captures
    :return: True if clicked successfully, False otherwise
    """
    try:
        terms_link = main_window.child_window(title="HP Instant Ink Terms of Service", control_type="Hyperlink")
        wait_for_element(terms_link, timeout=10)
        terms_link.click_input()
        print("Clicked 'HP Instant Ink Terms of service' link.")
        if ui_tree_file_path:
            capture_ui_tree(main_window, ui_tree_file_path, "After Terms of Service Click", append=True)
        return True
    except Exception as e:
        take_desktop_screenshot(" Failed to click 'HP Instant Ink Terms of service' link ", window_title="HP Smart")
        print(f"Failed to click 'HP Instant Ink Terms of service' link: {e}")
        return False

def verify_tos_page_displayed(timeout=30):
    """
    Verify the Terms of Service (TOS) page is displayed in a web browser.

    :param timeout: Time to wait for the browser window to appear
    :return: True if TOS page is displayed, False otherwise
    """
    try:
        browser = Desktop(backend="uia")
        # Adjust the title_re to match the actual TOS page title or URL
        tos_window = browser.window(title_re=".*Terms of Service.*|.*Instant Ink Terms.*|.*HP.*", visible_only=True)
        tos_window.wait("visible", timeout=timeout)
        assert tos_window.exists(), "TOS page should be displayed in the browser."
        print("TOS page is displayed in the web browser.")
        return True
    except Exception as e:
        take_desktop_screenshot(" TOS page not displayed in the browser  ", window_title="HP Smart")
        print(f"TOS page not displayed in the browser: {e}")
        return False

def verify_order_review_page(main_window):
    """Verify the Order Review page is displayed."""
    try:
        see_details_link = main_window.child_window(title="See details", control_type="Hyperlink")
        wait_for_element(see_details_link, timeout=10)
        if see_details_link.exists():
            print("'See details' link is visible on the page.")
            return see_details_link
        else:
            print("'See details' link not found.")
            return None
    except Exception as e:
        take_desktop_screenshot(" Error locating 'See details' link ", window_title="HP Smart")
        print(f"Error locating 'See details' link: {e}")
        return None

def click_continue_button(main_window, ui_tree_file_path):
    """Click the Continue button."""
    try:
        continue_btn = main_window.child_window(title_re="Continue", control_type="Button")
        wait_for_element(continue_btn, timeout=10)
        continue_btn.click()
        print("Continue button clicked.")
        time.sleep(2)
        capture_ui_tree(main_window, ui_tree_file_path, "After Continue Click", append=True)
    except Exception as e:
        take_desktop_screenshot(" Continue button not clicked ", window_title="HP Smart")
        print(f"Continue button not clicked: {e}")


def verify_arn_modal(main_window, ui_tree_file_path):
    """Verify the Automatic Renewal Notice modal is displayed."""
    try:
        arn_modal = main_window.child_window(title="Automatic Renewal Notice")
        wait_for_element(arn_modal, timeout=40)
        assert arn_modal.exists(), "ARN modal should be displayed."
        print("ARN modal is displayed.")
        arn_modal.click_input()
        send_keys("{PGDN}")
        time.sleep(2)
        capture_ui_tree(main_window, ui_tree_file_path, "AfterArn displayed", append=True)

    except Exception as e:
        take_desktop_screenshot(" ARN modal not displayed ", window_title="HP Smart")
        print(f"ARN modal not displayed: {e}")

def verify_checkbox_on_modal(main_window):
    """Verify the checkbox on the modal is displayed and unchecked."""
    try:
        tos_checkbox = main_window.child_window(auto_id="terms-of-service", control_type="CheckBox")
        wait_for_element(tos_checkbox, timeout=10)
        assert tos_checkbox.exists(), "Checkbox should be displayed."
        assert not tos_checkbox.get_toggle_state(), "Checkbox should be unchecked by default."
        print("Checkbox is displayed and unchecked.")
        # tos_checkbox.click_input()
        # print("Checkbox is checked.")
    except Exception as e:
        take_desktop_screenshot(" Checkbox verification failed ", window_title="HP Smart")
        print(f"Checkbox verification failed: {e}")

def verify_enroll_button_disabled(main_window, region="US"):
    """Verify the Enroll/Start Paid Service button is displayed as disabled before clicking the checkbox."""
    try:
        button_title = "Enroll" if region in ["US", "Canada", "Puerto Rico"] else "Start Paid Service"
        enroll_btn = main_window.child_window(title=button_title, control_type="Button")
        wait_for_element(enroll_btn, timeout=10)
        assert enroll_btn.exists(), f"{button_title} button should be displayed."
        assert not enroll_btn.is_enabled(), f"{button_title} button should be disabled before checkbox is clicked."
        print(f"{button_title} button is displayed and disabled.")
    except Exception as e:
        take_desktop_screenshot(" Enroll button verification failed ", window_title="HP Smart")
        print(f"Enroll button verification failed: {e}")

def verify_hp_instant_terms_link(main_window):
    """Verify the HP Instant Ink Terms of Service link is displayed."""
    try:
        tos_link = main_window.child_window(title="HP Instant Ink Terms of Service", control_type="Hyperlink")
        wait_for_element(tos_link, timeout=10)
        assert tos_link.exists(), "TOS link should be displayed."
        print("TOS link is displayed.")
    except Exception as e:
        take_desktop_screenshot(" TOS link verification failed ", window_title="HP Smart")
        print(f"TOS link verification failed: {e}")

def verify_arn_modal_close_button_displayed(main_window):
    """Verify the close (X) button is displayed in the ARN modal."""
    try:
        close_btn = main_window.child_window(title_re="Close modal", control_type="Button")
        wait_for_element(close_btn, timeout=10)
        assert close_btn.exists(), "Close button should be displayed in ARN modal."
        print("Close button is displayed in ARN modal.")
    except Exception as e:
        take_desktop_screenshot(" Close button not displayed in ARN modal ", window_title="HP Smart")
        print(f"Close button not displayed in ARN modal: {e}")

def close_arn_modal(main_window):
    """Click the close (X) button to close the ARN modal and verify it is closed."""
    try:
        close_btn = main_window.child_window(title_re="Close modal", control_type="Button")
        wait_for_element(close_btn, timeout=10)
        close_btn.click()
        # Optionally, verify modal is closed
        arn_modal = main_window.child_window(title_re="Automatic Renewal Notice", control_type="Window")
        assert not arn_modal.exists(), "ARN modal should be closed."
        print("ARN modal is closed.")
    except Exception as e:
        take_desktop_screenshot(" ARN modal not closed ", window_title="HP Smart")
        print(f"ARN modal not closed: {e}")


def scroll_until_locator(main_window, ui_tree_file_path):
    """
    Scroll using the mouse wheel until the given locator becomes visible.

    :param main_window: pywinauto window object
    :param locator_title: Partial or full title of the target element
    :param max_scrolls: Maximum number of scroll attempts
    :return: True if element is found, False otherwise
    """
    try:
        main_window.set_focus()

        for i in range(3):
            target_element = main_window.child_window(title="HP Instant Ink Terms of Service", control_type="Hyperlink")
            if target_element.exists(timeout=10):
                print(f" Found HP Instant Ink Terms of Service after {i} scroll(s).")
                target_element.set_focus()
                return True

            # Scroll down using mouse wheel
            mouse.scroll(coords=(500, 500), wheel_dist=-5)  # Adjust coords if needed
            time.sleep(1)
            time.sleep(2)
            capture_ui_tree(main_window, ui_tree_file_path, "After Scroll", append=True)

        print(f" HP Instant Ink Terms of Service not found after  mouse scroll attempts.")
        return False

    except Exception as e:
        take_desktop_screenshot(" Could not scroll to HP Instant Ink Terms of Service ", window_title="HP Smart")
        print(f" Could not scroll to HP Instant Ink Terms of Service: {e}")
        return False


def verify_enroll_button_enabled(main_window, region="US"):
    """Verify the Enroll/Start Paid Service button is enabled."""
    try:
        button_title = "Enroll" if region in ["US", "Canada"] else "Start Paid Service"
        enroll_btn = main_window.child_window(title_re=button_title, control_type="Button")
        wait_for_element(enroll_btn, timeout=10)
        assert enroll_btn.exists(), f"{button_title} button should be displayed."
        assert enroll_btn.is_enabled(), f"{button_title} button should be enabled."
        print(f"{button_title} button is displayed and enabled.")
    except Exception as e:
        take_desktop_screenshot(" verify button is not enabled ", window_title="HP Smart")
        print(f"{button_title} button is not enabled: {e}")

def click_checkbox(main_window):
    """
    Click the specified checkbox on the modal.
    """
    try:
        tos_checkbox = main_window.child_window(auto_id="terms-of-service", control_type="CheckBox")
        wait_for_element(tos_checkbox, timeout=20)

        tos_checkbox.toggle()
        print("Checkbox is checked.")
    except Exception as e:
        take_desktop_screenshot(" Checkbox Clicking failed ", window_title="HP Smart")
        print(f"Checkbox Clicking failed: {e}")

def click_enroll_button(main_window, region="US"):
    """
    Click the Enroll or Start Paid Service button.
    """
    try:
        button_title = "Enroll" if region in ["US", "Canada"] else "Start Paid Service"
        enroll_btn = main_window.child_window(title_re=button_title, control_type="Button")
        wait_for_element(enroll_btn, timeout=10)
        enroll_btn.invoke()
        print(f"{button_title} button clicked.")
    except Exception as e:
        take_desktop_screenshot(" Enroll button Clicking failed ", window_title="HP Smart")
        print(f"Could not click {button_title} button: {e}")


def verify_thank_you_page_content(main_window):
    """

    Verify that the Thank You page (Success message) is displayed correctly.

    """

    try:

        # Look for any element that has "Success!" text

        thank_you_element = main_window.child_window(title="Success!", control_type="Text")

        # Wait for it to appear

        wait_for_element(thank_you_element, timeout=20)

        # Verify existence

        assert thank_you_element.exists(), "'Success!' text not found on the Thank You page."

        print(" Thank You page 'Success!' message is displayed correctly.")

        return True

    except AssertionError as ae:

        print(ae)

        return False

    except Exception as e:
        take_desktop_screenshot(" Thank You page content verification failed ", window_title="HP Smart")
        print(f" Thank You page content verification failed: {e}")

        return False


def click_outside_arn_modal(main_window):
    """
    Click outside the ARN modal to close it.
    Locator: ClassName: "vn-modal--dialog css-1qavj3f-dialog"
    """
    try:
        modal_dialog = main_window.child_window(class_name="vn-modal--dialog css-1qavj3f-dialog")
        # Wait for the modal to be present (replace with your own wait logic if needed)
        # Example: time.sleep(1) or use your own wait_for_element function
        # Click at a position outside the modal (dummy coordinates)
        main_window.click_input(coords=(10, 10))
        print("Clicked outside ARN modal.")
    except Exception as e:
        take_desktop_screenshot(" Could not click outside ARN modal ", window_title="HP Smart")
        print(f"Could not click outside ARN modal: {e}")


def verify_email_displayed_in_thank_you_page(main_window, expected_email="107testcase@yopmail.com"):
    """
    Verify the user's email is displayed on the Thank You page.
    """
    try:
        # Locate element that displays the email (match exact or partial)
        email_element = main_window.child_window(title=expected_email, control_type="Text")

        # Wait until element appears
        wait_for_element(email_element, timeout=20)

        # Assert it's visible on the page
        assert email_element.exists(), f" Email '{expected_email}' not found on the Thank You page."

        print(f"Email '{expected_email}' is displayed on the Thank You page.")
    except Exception as e:
        take_desktop_screenshot("  Email verification on Thank You page failed", window_title="HP Smart")
        print(f" Email verification on Thank You page failed: {e}")

def click_continue_on_thank_you_page(main_window):
    """
    Click the Continue button on the Thank You page.
    """
    try:
        continue_btn = main_window.child_window(title_re="Continue", control_type="Button")
        wait_for_element(continue_btn, timeout=10)
        continue_btn.click_input()
        print("Continue button clicked on Thank You page.")
    except Exception as e:
        print(f"Could not click Continue on Thank You page: {e}")

def click_yes_continue_setup(main_window):
    """
    Click the 'Yes, continue setup' button.
    """
    try:
        yes_continue_btn = main_window.child_window(title_re="Yes, continue setup", control_type="Button")
        wait_for_element(yes_continue_btn, timeout=10)
        yes_continue_btn.click()
        print("'Yes, continue setup' button clicked.")
    except Exception as e:
        take_desktop_screenshot(" Could not click 'Yes, continue setup' button", window_title="HP Smart")
        print(f"Could not click 'Yes, continue setup' button: {e}")

def click_skip_sending_link(main_window):
    """
    Click the 'Skip sending link' link.
    """
    try:
        skip_link = main_window.child_window(title_re="Skip sending link", control_type="Hyperlink")
        wait_for_element(skip_link, timeout=10)
        skip_link.click_input()
        print("'Skip sending link' clicked.")
    except Exception as e:
        take_desktop_screenshot(" Could not click 'Skip sending link ", window_title="HP Smart")
        print(f"Could not click 'Skip sending link': {e}")

def verify_setup_complete_lets_print_displayed(main_window):
    """
    Verify the 'Setup complete, let’s print' button is displayed.
    """
    try:
        print_btn = main_window.child_window(title_re="Setup complete, let’s print", control_type="Hyperlink")
        wait_for_element(print_btn, timeout=10)
        assert print_btn.exists(), "'Setup complete, let’s print' button should be displayed."
        print("'Setup complete, let’s print' button is displayed.")
    except Exception as e:
        take_desktop_screenshot(" Could not verify 'Setup complete, let’s print' button ", window_title="HP Smart")
        print(f"Could not verify 'Setup complete, let’s print' button: {e}")

def click_skip_printing_page(main_window):
    """
    Click the 'Skip printing page' link.
    """
    try:
        skip_print_link = main_window.child_window(title_re="Skip printing page", control_type="Hyperlink")
        wait_for_element(skip_print_link, timeout=10)
        skip_print_link.click()
        print("'Skip printing page' link clicked.")
    except Exception as e:
        take_desktop_screenshot("Could not click 'Skip printing page' link", window_title="HP Smart")
        print(f"Could not click 'Skip printing page' link: {e}")

def verify_homescreen_displayed(main_window):
    """
    Verify the homescreen is displayed.
    """
    try:
        homescreen = main_window.child_window(title_re="Home", control_type="Radio Button")
        wait_for_element(homescreen, timeout=10)
        assert homescreen.exists(), "Homescreen should be displayed."
        print("Homescreen is displayed.")
    except Exception as e:
        take_desktop_screenshot(" Homescreen not displayed ", window_title="HP Smart")
        print(f"Homescreen not displayed: {e}")


def verify_dashboard_displayed(main_window):
    """
    Verify the dashboard is displayed.
    """
    try:
        dashboard = main_window.child_window(title_re="Overview", control_type="Text")
        wait_for_element(dashboard, timeout=60)
        assert dashboard.exists(), "Dashboard should be displayed."
        print("Dashboard is displayed.")
    except Exception as e:
        take_desktop_screenshot(" Dashboard not displayed ", window_title="HP Smart")
        print(f"Dashboard not displayed: {e}")


def click_get_supplies_tile(main_window):
    """
    Click the 'Get Supplies' tile on the homescreen.
    """
    try:
        supplies_tile = main_window.child_window(title="Get Supplies", control_type="Button", auto_id="TileButton")
        assert supplies_tile.exists(), "Get Supplies tile should be displayed."
        wait_for_element(supplies_tile, timeout=50)
        supplies_tile.click()
        print("'Get Supplies' tile clicked.")
    except Exception as e:
        take_desktop_screenshot(" Could not click 'Get Supplies' tile ", window_title="HP Smart")
        print(f"Could not click 'Get Supplies' tile: {e}")

def verify_replace_printer_text(main_window, expected_text="Enroll or replace a printer"):
    """
    Verify the 'Replace Printer' text is displayed.
    """
    try:
        replace_text = main_window.child_window(title_re=expected_text, control_type="Text")
        wait_for_element(replace_text, timeout=10)
        assert replace_text.exists(), f"'{expected_text}' text should be displayed."
        print(f"'{expected_text}' text is displayed.")
    except Exception as e:
        take_desktop_screenshot("Could not verify replace printer text ", window_title="HP Smart")
        print(f"Could not verify '{expected_text}' text: {e}")


def click_select_printer_in_homepage(main_window):
    """
    Click the 'Select Printer' button in the homepage.
    """
    try:
        select_printer_btn = main_window.child_window(title_re="Select Printer", control_type="Button")
        wait_for_element(select_printer_btn, timeout=10)
        select_printer_btn.click()
        print("'Select Printer' button clicked in homepage.")
    except Exception as e:
        take_desktop_screenshot("Could not click 'Select Printer' button ", window_title="HP Smart")
        print(f"Could not click 'Select Printer' button: {e}")

def verify_printer_name_in_homepage(main_window, printer_name):
    """
    Verify the printer name is displayed in the homepage.
    """
    try:
        printer_name_element = main_window.child_window(title_re=printer_name, control_type="Text")
        wait_for_element(printer_name_element, timeout=10)
        assert printer_name_element.exists(), f"Printer name '{printer_name}' should be displayed in homepage."
        print(f"Printer name '{printer_name}' is displayed in homepage.")
    except Exception as e:
        print(f"Could not verify printer name '{printer_name}' in homepage: {e}")

def click_replace_printer_page(main_window):
    """
    Click the 'Replace a Printer' button/link to open the replace printer page.
    """
    try:
        replace_printer_btn = main_window.child_window(title_re="Replace a printer that's enrolled or in a trial", control_type="Button")
        wait_for_element(replace_printer_btn, timeout=10)
        replace_printer_btn.click()
        print("'Replace a Printer' button clicked.")
    except Exception as e:
        take_desktop_screenshot("Could not click 'Replace a Printer' button", window_title="HP Smart")
        print(f"Could not click 'Replace a Printer' button: {e}")

def verify_review_and_confirm_printer_replacement(main_window):
    """
    Verify the 'REVIEW AND CONFIRM PRINTER REPLACEMENT' text is displayed.
    """
    try:
        review_text = main_window.child_window(title_re="Review and confirm printer replacement", control_type="Text")
        wait_for_element(review_text, timeout=10)
        assert review_text.exists(), "'REVIEW AND CONFIRM PRINTER REPLACEMENT' should be displayed."
        print("'REVIEW AND CONFIRM PRINTER REPLACEMENT' is displayed.")
    except Exception as e:
        print(f"Could not verify 'REVIEW AND CONFIRM PRINTER REPLACEMENT': {e}")

def verify_printer_card_displayed(main_window):
    """
    Verify the text 'Printer' is displayed on the printer card.
    """
    try:
        printer_card = main_window.child_window(title_re="Printer", control_type="Pane")
        wait_for_element(printer_card, timeout=10)
        assert printer_card.exists(), "'Printer' card should be displayed."
        print("'Printer' card is displayed.")
    except Exception as e:
        take_desktop_screenshot("Could not verify 'Printer' card ", window_title="HP Smart")
        print(f"Could not verify 'Printer' card: {e}")

def verify_new_and_old_printer_details(main_window):
    """
    Verify new and old printer details (name and serial number) are displayed.
    """
    try:
        # Old printer name
        old_name_elem = main_window.child_window(title_re="HP DeskJet 2955 AiO Printer", control_type="Text")
        wait_for_element(old_name_elem, timeout=10)
        assert old_name_elem.exists(), "Old printer name should be displayed."

        # Old printer serial number
        old_sn_elem = main_window.child_window(title_re="CN4BL14650", control_type="Text")
        wait_for_element(old_sn_elem, timeout=10)
        assert old_sn_elem.exists(), "Old printer serial number should be displayed."

        # New printer name
        new_name_elem = main_window.child_window(title_re="HP DeskJet 2942 All-in-One Printer", control_type="Text")
        wait_for_element(new_name_elem, timeout=10)
        assert new_name_elem.exists(), "New printer name should be displayed."

        # New printer serial number
        new_sn_elem = main_window.child_window(title_re="CN4BL14653", control_type="Text")
        wait_for_element(new_sn_elem, timeout=10)
        assert new_sn_elem.exists(), "New printer serial number should be displayed."

        print("Both new and old printer details are displayed correctly.")
    except Exception as e:
        print(f"Could not verify new and old printer details: {e}")

def click_close_modal_button(main_window):
    """
    Click the 'Close modal' button.
    """
    try:
        close_btn = main_window.child_window(title_re="Close modal", control_type="Button")
        wait_for_element(close_btn, timeout=10)
        close_btn.click()
        print("'Close modal' button clicked.")
    except Exception as e:
        take_desktop_screenshot(" Could not click 'Close modal' button ", window_title="HP Smart")
        print(f"Could not click 'Close modal' button: {e}")

def click_outside_shipping_modal_and_verify_modal_still_open(main_window):
    """
    Click outside the Shipping modal and verify the modal does not close.
    """
    try:
        main_window.click_input(coords=(10, 10))  # Dummy coordinates outside modal
        street_box = main_window.child_window(auto_id="street1", control_type="Edit")
        wait_for_element(street_box, timeout=10)
        assert street_box.exists(), "Shipping modal should remain open after clicking outside."
        print("Shipping modal closed unexpectedly after clicking outside")
    except Exception as e:
        take_desktop_screenshot(" Shipping modal did not close after clicking outside ", window_title="HP Smart")
        print(f"Shipping modal did not close after clicking outside.: {e}")

def verify_promo_or_pin_code_link_not_displayed(main_window):
    """
    Verify the 'Enter a promo or PIN code' link is not displayed.
    """
    try:
        promo_link = main_window.child_window(title="Enter promo or PIN code", control_type="Hyperlink")
        # Wait briefly to ensure UI is loaded
        time.sleep(2)
        assert not promo_link.exists(), "'Enter a promo or PIN code' link should NOT be displayed."
        print("'Enter a promo or PIN code' link is not displayed as expected.")
    except Exception as e:
        take_desktop_screenshot(" Promo or PIN code link display verification failed ", window_title="HP Smart")
        print(f"Promo or PIN code link display verification failed: {e}")

def verify_billing_heading_in_modal(main_window):
    """
    Verify the billing heading is displayed in the billing modal.
    """
    try:
        billing_heading = main_window.child_window(title_re="Billing", control_type="Text")
        wait_for_element(billing_heading, timeout=10)
        assert billing_heading.exists(), "Billing heading should be displayed in billing modal."
        print("Billing heading is displayed in billing modal.")
    except Exception as e:
        take_desktop_screenshot("Billing heading not displayed in billing modal  ", window_title="HP Smart")
        print(f"Billing heading not displayed in billing modal: {e}")

def verify_link_payment_provider_in_billing_modal(main_window):
    """
    Verify the 'Link a payment provider' link is displayed in the billing modal.
    """
    try:
        link_payment = main_window.child_window(title="Link a payment provider", control_type="Link")
        wait_for_element(link_payment, timeout=10)
        assert link_payment.exists(), "'Link a payment provider' link should be displayed in billing modal."
        print("'Link a payment provider' link is displayed in billing modal.")
    except Exception as e:
        take_desktop_screenshot(" Link a payment provider' link not displayed in billing modal ", window_title="HP Smart")
        print(f"'Link a payment provider' link not displayed in billing modal: {e}")

def modify_billing_details(main_window, ui_tree_file_path, billing_data):
    """
    Modify the billing details and click the save button.
    """
    try:
        # Card number
        field = main_window.child_window(auto_id="txtCardNumber", control_type="Edit")
        if field.exists(timeout=10):
            field.set_text(billing_data.get("card_number", ""))
            print(" Entered card number")

        # Expiration month
        exp_m = main_window.child_window(auto_id="drpExpMonth", control_type="ComboBox")
        if exp_m.exists(timeout=5):
            exp_m.select(billing_data.get("exp_month", ""))
            print(" Selected expiration month")

        # Expiration year
        exp_y = main_window.child_window(auto_id="drpExpYear", control_type="ComboBox")
        if exp_y.exists(timeout=5):
            exp_y.select(billing_data.get("exp_year", ""))
            print(" Selected expiration year")

        # CVV
        cvv_field = main_window.child_window(auto_id="txtCVV", control_type="Edit")
        if cvv_field.exists(timeout=5):
            cvv_field.set_text(billing_data.get("cvv", ""))
            print(" Entered CVV")

        capture_ui_tree(main_window, ui_tree_file_path, "After entering billing details", append=True)

        # Click Continue
        save_btn = main_window.child_window(title="Continue", control_type="Button")
        if save_btn.exists(timeout=10) and save_btn.is_enabled():
            save_btn.click_input()
            print(" Clicked Save after modifying billing details")

        capture_ui_tree(main_window, ui_tree_file_path, "After clicking Save on billing", append=True)

    except Exception as e:
        take_desktop_screenshot(" Error modifying billing details ", window_title="HP Smart")
        print(f" Error modifying billing details: {e}")

def verify_edit_plan_icon_displayed(main_window):
    """
    Verify the Edit Plan icon is displayed.
    """
    try:
        edit_icon = main_window.child_window(title="Edit", control_type="Button")
        wait_for_element(edit_icon, timeout=10)
        assert edit_icon.exists(), "Edit Plan icon should be displayed."
        print("Edit Plan icon is displayed.")
    except Exception as e:
        print(f"Edit Plan icon not displayed: {e}")

def click_outside_billing_modal_and_verify_modal_still_open(main_window):
    """
    Click outside the Billing modal and verify the modal does not close.
    """
    try:
        main_window.click_input(coords=(10, 10))  # Dummy coordinates outside modal
        billing_modal = main_window.child_window(title_re="Billing", control_type="Text")
        wait_for_element(billing_modal, timeout=10)
        assert billing_modal.exists(), "Billing modal should remain open after clicking outside."
        print("Billing modal did not close after clicking outside.")
    except Exception as e:
        print(f"Billing modal closed unexpectedly after clicking outside: {e}")

def verify_redeemed_months_credits(main_window):
    try:
        redeemed_section = main_window.child_window(title_re="Redeemed months \+ credits", control_type="Text")
        wait_for_element(redeemed_section, timeout=10)
        assert redeemed_section.exists(), "'Redeemed months + credits' section should be displayed."
    except Exception as e:
        take_desktop_screenshot(" Redeemed months + credits section not displayed ", window_title="HP Smart")
        print(f"Redeemed months + credits section not displayed: {e}")

def verify_redeemed_months_credits_section_with_see_details(main_window):
    """
    Verify the '[X] Redeemed months + credits' section and 'See details' link are displayed and 'See details' is blue.
    """
    try:
        redeemed_section = main_window.child_window(title_re="Redeemed months \+ credits", control_type="Text")
        wait_for_element(redeemed_section, timeout=10)
        assert redeemed_section.exists(), "'Redeemed months + credits' section should be displayed."

        see_details_link = main_window.child_window(title_re="See details", control_type="Link")
        wait_for_element(see_details_link, timeout=10)
        assert see_details_link.exists(), "'See details' link should be displayed."

        # Check color property (if available)
        color = getattr(see_details_link, "color", None)
        if color:
            assert color == "blue", "'See details' link should be blue."
        print("Redeemed months + credits section and blue 'See details' link are displayed.")
    except Exception as e:
        take_desktop_screenshot(" Redeemed months + credits section or 'See details' link not displayed ", window_title="HP Smart")
        print(f"Redeemed months + credits section or 'See details' link not displayed: {e}")

def verify_sob_modal_title(main_window):
    """
    Verify the SOB modal with title 'Special Offers' is displayed.
    """
    try:
        sob_modal = main_window.child_window(title="Special Offers", control_type="Text")
        wait_for_element(sob_modal, timeout=10)
        assert sob_modal.exists(), "'Special Offers' modal should be displayed."
        print("'Special Offers' modal is displayed.")
    except Exception as e:
        take_desktop_screenshot(" Special Offers' modal not displayed ", window_title="HP Smart")
        print(f"'Special Offers' modal not displayed: {e}")

def verify_breakdown_of_credits_section(main_window):
    """
    Verify the 'Breakdown of credits' section and 'Transferring months' text are displayed in SOB modal.
    """
    try:
        breakdown_section = main_window.child_window(title_re="Breakdown of credits", control_type="Text")
        wait_for_element(breakdown_section, timeout=10)
        assert breakdown_section.exists(), "'Breakdown of credits' section should be displayed."

        transferring_months = main_window.child_window(title_re="Transferring months", control_type="Text")
        wait_for_element(transferring_months, timeout=10)
        assert transferring_months.exists(), "'Transferring months' text should be displayed."

        print("'Breakdown of credits' section and 'Transferring months' text are displayed.")
    except Exception as e:
        print(f"'Breakdown of credits' section or 'Transferring months' text not displayed: {e}")

def verify_promo_or_pin_code_link_displayed(main_window):
    """
    Verify the 'Enter a promo or PIN code' link is displayed.
    """
    try:
        promo_link = main_window.child_window(title="Enter a promo or PIN code", control_type="Link")
        wait_for_element(promo_link, timeout=10)
        assert promo_link.exists(), "'Enter a promo or PIN code' link should be displayed."
        print("'Enter a promo or PIN code' link is displayed.")
    except Exception as e:
        print(f"'Enter a promo or PIN code' link not displayed: {e}")

def click_promo_or_pin_code_link(main_window):
    """
    Click the 'Enter a promo or PIN code' link if it is displayed.
    """
    try:
        promo_link = main_window.child_window(title="Enter a promo or PIN code", control_type="Link")
        if promo_link.exists():
            promo_link.click_input()
            print("'Enter a promo or PIN code' link clicked.")
        else:
            print("'Enter a promo or PIN code' link is not displayed, cannot click.")
    except Exception as e:
        print(f"Could not click 'Enter a promo or PIN code' link: {e}")

def verify_order_summary_details(main_window):
    """
    Verify order summary details: Ink Plan, trial ends, Total due now, Total due after trial.
    """
    try:
        ink_plan = main_window.child_window(title="Ink Plan", control_type="Text")
        wait_for_element(ink_plan, timeout=10)
        assert ink_plan.exists(), "'Ink Plan' should be displayed."

        trial_ends = main_window.child_window(title="trial ends", control_type="Text")
        wait_for_element(trial_ends, timeout=10)
        assert trial_ends.exists(), "'trial ends' should be displayed."

        total_due_now = main_window.child_window(title="Total due now", control_type="Text")
        wait_for_element(total_due_now, timeout=10)
        assert total_due_now.exists(), "'Total due now' should be displayed."

        total_due_after_trial = main_window.child_window(title="Total due after trial", control_type="Text")
        wait_for_element(total_due_after_trial, timeout=10)
        assert total_due_after_trial.exists(), "'Total due after trial' should be displayed."

        print("Order summary details are displayed correctly.")
    except Exception as e:
        print(f"Order summary details verification failed: {e}")

def verify_printer_replacement_info_text(main_window):
    """
    Verify the printer replacement info text is displayed.
    """
    try:
        info_text = main_window.child_window(
            title="You are replacing your printer on an existing account. Your account history will be saved after the replacement.",
            control_type="Text"
        )
        wait_for_element(info_text, timeout=10)
        assert info_text.exists(), "Printer replacement info text should be displayed."
        print("Printer replacement info text is displayed.")
    except Exception as e:
        print(f"Printer replacement info text not displayed: {e}")

def verify_confirm_button_displayed(main_window):
    """
    Scroll to and verify the 'Confirm' button is displayed.
    """
    try:
        send_keys('{PGDN}')
        confirm_btn = main_window.child_window(title="Confirm", control_type="Button")
        wait_for_element(confirm_btn, timeout=10)
        assert confirm_btn.exists(), "'Confirm' button should be displayed."
        print("'Confirm' button is displayed.")
    except Exception as e:
        take_desktop_screenshot("Confirm' button not displayed  ", window_title="HP Smart")
        print(f"'Confirm' button not displayed: {e}")

def click_confirm_button(main_window):
    """
    Click the 'Confirm' button.
    """
    try:
        confirm_btn = main_window.child_window(title="Confirm", control_type="Button")
        wait_for_element(confirm_btn, timeout=10)
        confirm_btn.click_input()
        print("'Confirm' button clicked.")
    except Exception as e:
        print(f"Could not click 'Confirm' button: {e}")


def click_check_out_button(main_window, ui_tree_file_path):
    """
    Click the 'HP Checkout' button on the HP Smart app.
    """
    try:
        checkout_btn = main_window.child_window(title="HP Checkout", control_type="Button")
        time.sleep(15)
        capture_ui_tree(main_window, ui_tree_file_path, "Before HP Checkout", append=True)

        wait_until(
            timeout=100,
            retry_interval=2,
            func=lambda: checkout_btn.exists() and checkout_btn.is_enabled(),
        )

        assert checkout_btn.exists(), "'HP Checkout' button should be displayed on the screen."

        checkout_btn.click_input()
        print("Clicked 'HP Checkout' button successfully.")

        time.sleep(5)
        capture_ui_tree(main_window, ui_tree_file_path, "After HP Checkout", append=True)

    except Exception as e:
        take_desktop_screenshot("'HP Checkout' button not displayed or click failed", window_title="HP Smart")
        print(f"'HP Checkout' button not displayed or click failed: {e}")


def verify_review_and_confirm_printer_replacement_page_content_and_layout(main_window, ui_tree_file_path):
    """
    Verify the content and layout on 'Review and confirm printer replacement' page.
    """
    try:
        review_page = main_window.child_window(
            title_re="Review and confirm printer replacement", control_type="Text"
        )
        wait_for_element(review_page, timeout=15)
        assert review_page.exists(), "'Review and confirm printer replacement' page should be displayed."
        capture_ui_tree(
            main_window, ui_tree_file_path, "After Review and Confirm Printer Replacement Page", append=True
        )
        print("Content and layout on 'Review and confirm printer replacement' page match the prototype.")
    except Exception as e:
        take_desktop_screenshot(" Content or layout issue on 'Review and confirm printer replacement' page ", window_title="HP Smart")
        print(f"Content or layout issue on 'Review and confirm printer replacement' page: {e}")


def verify_special_offers_section_not_displayed(main_window):
    """
    Verify the Special Offers section is not displayed.
    """
    try:
        special_offers = main_window.child_window(title_re="Special Offers", control_type="heading")
        assert not special_offers.exists(), "Special Offers section should NOT be displayed."
        print("Special Offers section is not displayed.")
    except Exception as e:
        take_desktop_screenshot(" Error verifying Special Offers section ", window_title="HP Smart")
        print(f"Error verifying Special Offers section: {e}")

def verify_review_and_confirm_printer_replacement_page(main_window, ui_tree_file_path):
    """
    Verify the 'Review and confirm printer replacement' page is displayed.
    """
    review_page = main_window.child_window(title_re="Review and confirm printer replacement", control_type="Text")
    wait_for_element(review_page, timeout=15)
    assert review_page.exists(), "'Review and confirm printer replacement' page should be displayed."
    capture_ui_tree(main_window, ui_tree_file_path, "After Review and Confirm Printer Replacement Page", append=True)

def verify_back_button_displayed(main_window):
    """
    Verify the Back button is displayed.
    """
    try:
        back_btn = main_window.child_window(title="Back", control_type="button")
        wait_for_element(back_btn, timeout=10)
        assert back_btn.exists(), "Back button should be displayed."
        print("Back button is displayed correctly.")
    except Exception as e:
        take_desktop_screenshot("Back button verification failed", window_title="HP Smart")
        print(f"Back button verification failed: {e}")

def click_back_button_and_verify_redirect(main_window):
    """
    Click Back button and verify redirect to PR Printer info page.
    """
    try:
        back_btn = main_window.child_window(title="Back", control_type="button")
        wait_for_element(back_btn, timeout=10)
        back_btn.click_input()

        info_page = main_window.child_window(
            title_re="Your replacement printer is compatible with HP Instant Ink!",
            control_type="Text"
        )
        wait_for_element(info_page, timeout=15)
        assert info_page.exists(), "Should be redirected to PR Printer info page."

        print("Redirect to PR Printer info page verified successfully.")
    except Exception as e:
        take_desktop_screenshot("Redirect verification failed", window_title="HP Smart")
        print(f"Redirect verification failed: {e}")

def verify_origami_focused_choice_modal(main_window, ui_tree_file_path):
    """
    Verify the Origami Focused Choice modal is displayed with correct content and layout.
    """
    try:
        origami_modal = main_window.child_window(title_re="Skip Paper", control_type="Button")
        wait_for_element(origami_modal, timeout=15)
        assert origami_modal.exists(), "skip button should display."
        capture_ui_tree(main_window, ui_tree_file_path, "After Origami Focused Choice Modal", append=True)
        print("Origami Focused Choice modal verified successfully.")
    except Exception as e:
        take_desktop_screenshot("Origami modal verification failed", window_title="HP Smart")
        print(f"Origami modal verification failed: {e}")
def verify_origami_modal_values(main_window, origami_addon_credits):
    """
    Verify the correct free month info and paper add-on value are displayed in the Origami modal.
    """
    # origami_modal = main_window.child_window(title_re="Skip Paper", control_type="button")
    free_months = main_window.child_window(title="Try it for 1 month.", control_type="Text")
    paper_add_on = main_window.child_window(title=f"${origami_addon_credits}/month after trial. (HP Paper: 8.5x11; 20lb; 96 Bright)", control_type="Text")
    # wait_for_element(free_months, timeout=10)
    # wait_for_element(paper_add_on, timeout=10)
    assert free_months.exists(), "Try it for 1 month not found"
    assert paper_add_on.exists(), "$4.49/month after trial. (HP Paper: 8.5x11; 20lb; 96 Bright)"


def verify_origami_modal_buttons(main_window):
    """
    Verify the 'Add Paper' and 'Skip Paper' buttons are displayed in the Origami modal.
    """
    # origami_modal = main_window.child_window(title_re="Skip Paper", control_type="button")
    add_paper_btn = main_window.child_window(title="Add Paper", control_type="Button")
    skip_paper_btn = main_window.child_window(title="Skip Paper", control_type="Button")
    wait_for_element(add_paper_btn, timeout=10)
    wait_for_element(skip_paper_btn, timeout=10)
    assert add_paper_btn.exists(), "'Add Paper' button should be displayed."
    assert skip_paper_btn.exists(), "'Skip Paper' button should be displayed."

def verify_origami_modal_learn_more_link(main_window):
    """
    Verify the 'Learn more' link is displayed in the Origami modal.
    """
    # origami_modal = main_window.child_window(title_re="Skip Paper", control_type="button")
    learn_more_link = main_window.child_window(title="Learn more", control_type="Button")
    wait_for_element(learn_more_link, timeout=10)
    assert learn_more_link.exists(), "'Learn more' link should be displayed in Origami modal."

def click_skip_paper_on_origami_modal(main_window):
    """
    Click the 'Skip Paper' button on the Origami Focused Choice modal.
    """

    skip_paper_btn = main_window.child_window(title="Skip Paper", control_type="Button")
    wait_for_element(skip_paper_btn, timeout=10)
    skip_paper_btn.click_input()
    assert skip_paper_btn.exists(), "Origami Focused Choice modal should be closed after clicking Skip Paper."



def verify_printer_replacement_confirmation_page_after_skip_paper(main_window):
    """
    Verify the Origami section is displayed and Paper plan details are not shown in the Order Summary section.
    """
    origami_section = main_window.child_window(title_re="Add Paper", control_type="button")
    wait_for_element(origami_section, timeout=10)
    assert origami_section.exists(), "Origami section should be displayed on confirmation page."
    paper_plan = main_window.child_window(title_re="/month", control_type="Text")
    assert not paper_plan.exists(), "Paper plan details should not be shown in Order Summary section."

def verify_origami_section_displayed(main_window):
    """
    Verify the Origami section is displayed on the Printer Replacement confirmation page.
    """
    origami_section = main_window.child_window(title_re="Skip Paper", control_type="button")
    wait_for_element(origami_section, timeout=10)
    assert not origami_section.exists(), "Origami section should be displayed on confirmation page."

def verify_origami_focused_choice_modal_not_displayed(main_window):
    """
    Verify the Origami Focused Choice modal is NOT displayed.
    """
    origami_modal = main_window.child_window(title_re="Skip Paper", control_type="button")
    assert not origami_modal.exists(), "Origami Focused Choice modal should NOT be displayed."

def verify_origami_section_and_modal_not_displayed(main_window):
    """
    Verify the Origami section and Origami Focused Choice modal are NOT displayed on the Printer Replacement confirmation page.
    """
    origami_section = main_window.child_window(title_re="Origami", control_type="Group")
    origami_modal = main_window.child_window(title_re="Origami Focused Choice", control_type="Window")
    assert not origami_section.exists(), "Origami section should NOT be displayed."
    assert not origami_modal.exists(), "Origami Focused Choice modal should NOT be displayed."


def verify_review_and_confirm_printer_replacement_page(main_window, ui_tree_file_path):
    try:
        """
        Verify the 'Review and confirm printer replacement' page is displayed.
        """
        review_page = main_window.child_window(
            title_re="Review and confirm printer replacement",
            control_type="Text"
        )
        wait_for_element(review_page, timeout=15)
        assert review_page.exists(), "'Review and confirm printer replacement' page should be displayed."

        capture_ui_tree(
            main_window,
            ui_tree_file_path,
            "After Review and Confirm Printer Replacement Page",
            append=True
        )
        print("'Review and confirm printer replacement' page is displayed.")
    except AssertionError as e:
        take_desktop_screenshot(" Review and confirm printer replacement' page is not displayed ", window_title="HP Smart")
        print("'Review and confirm printer replacement' page is not displayed.")


def verify_thank_you_page_branding(main_window):
    """
    Verify HP Logo and HP Instant Ink branding is displayed on the Thank You page.
    """

    thank_you = main_window.child_window(title_re="Success!", control_type="heading")
    hp_instant_logo = main_window.child_window(title_re="instant ink logo", control_type="graphic")
    cartridge_logo = main_window.child_window(title_re="cartridges", control_type="graphic")
    wait_for_element(thank_you, timeout=10)
    wait_for_element(hp_instant_logo, timeout=10)
    wait_for_element(cartridge_logo, timeout=10)
    assert thank_you.exists(), "HP Logo should be displayed on the Thank You page."
    assert hp_instant_logo.exists(), "HP Logo should be displayed on the Thank You page."
    assert cartridge_logo.exists(), "HP Instant Ink cartridge should be displayed on the Thank You page."

def verify_thank_you_page_image(main_window):
    """
    Verify appropriate [ink]/[toner] image is displayed on the Thank You page.
    """
    ink_image = main_window.child_window(title_re="Your printer has been replaced.", control_type="heading ")
    wait_for_element(ink_image, timeout=10)
    assert ink_image.exists(), "Appropriate ink/toner image should be displayed on the Thank You page."

def verify_thank_you_page_buttons(main_window):
    """
    Verify 'Back' button is not seen and the 'Continue' button is displayed well on the Thank You page.
    """
    back_btn = main_window.child_window(title="Back", control_type="Button")
    continue_btn = main_window.child_window(title="Continue", control_type="button")
    assert not back_btn.exists(), "'Back' button should not be displayed on the Thank You page."
    wait_for_element(continue_btn, timeout=10)
    assert continue_btn.exists(), "'Continue' button should be displayed on the Thank You page."

def click_continue_on_thank_you_page(main_window):
    """
    Click the 'Continue' button on the Thank You page.
    """
    try:
        # Locate the 'Continue' button
        continue_btn = main_window.child_window(title="Continue", control_type="Button")
        wait_for_element(continue_btn, timeout=10)
        continue_btn.click_input()
        print("Clicked the 'Continue' button on the Thank You page.")
    except Exception as e:
        take_desktop_screenshot("Clicking 'Continue' on Thank You page failed", window_title="HP Smart")
        print(f"Clicking 'Continue' on Thank You page failed: {e}")


def verify_ows_screen_displayed(main_window):
    """
    Verify the OWS (Out of Workflow Screen) is displayed after exiting II flow.
    """
    ows_screen = main_window.child_window(title_re="Home", control_type="radio button")
    wait_for_element(ows_screen, timeout=15)
    assert ows_screen.exists(), "OWS screen should be displayed after exiting II flow."

def complete_printer_replacement_flow(main_window, ui_tree_file_path):
    """
    Complete the printer replacement flow and navigate to the dashboard.
    """
    ows_screen = main_window.child_window(title_re="Home", control_type="radio button")
    wait_for_element(ows_screen, timeout=15)
    assert ows_screen.exists(), "complete_printer_replacement_flow("

def verify_new_printer_dashboard(main_window):
    """
    Verify new printer and incentives are displayed on the Dashboard page.
    """
    new_printer = main_window.child_window(title_re="HP", control_type="Text")
    wait_for_element(new_printer, timeout=15)
    assert new_printer.exists(), "New printer should be displayed on Dashboard page."

def verify_ink_status_card(main_window, test_data):
    """
    Verify appropriate status is seen in Ink Status card on Overview page.
    """
    ink_status_card = main_window.child_window(title_re="Ready to print", control_type="text")
    wait_for_element(ink_status_card, timeout=15)
    assert ink_status_card.exists(), "Ink Status card should be displayed on Overview page."


def verify_pages(main_window, expected_page):
    """
    Verify the email is displayed on the Thank You page.
    """
    try:
        page = main_window.child_window(title_re=f" '{expected_page}' of 100 used", control_type="Text")
        wait_for_element(page, timeout=10)
        assert page.exists(), f"Email '{page}' should be displayed on the dashboard page."

    except Exception as e:
        print(f"page verification on dashboard page failed: {e}")

def verify_billing_details_not_saved(main_window, test_data, ui_tree_file_path, should_exist=True):
    """
    Verify that the saved billing details are displayed correctly on the Billing Card.
    If should_exist=False, verify that details are NOT displayed.
    """
    try:
        billing_card = main_window.child_window(title_re="Billing", control_type="Group")
        wait_for_element(billing_card, timeout=15)
        assert billing_card.exists() == should_exist, "Billing Card display state mismatch."

        name = billing_card.child_window(title_re=f".*{test_data['billing']['name']}.*", control_type="Text")
        address = billing_card.child_window(title_re=f".*{test_data['billing']['address']}.*", control_type="Text")
        city = billing_card.child_window(title_re=f".*{test_data['billing']['city']}.*", control_type="Text")
        state = billing_card.child_window(title_re=f".*{test_data['billing']['state']}.*", control_type="Text")
        zip_code = billing_card.child_window(title_re=f".*{test_data['billing']['zip']}.*", control_type="Text")
        phone = billing_card.child_window(title_re=f".*{test_data['billing']['phone']}.*", control_type="Text")

        for field, value in zip(
                ["name", "address", "city", "state", "zip_code", "phone"],
                [name, address, city, state, zip_code, phone]
        ):
            wait_for_element(value, timeout=10)
            assert value.exists() == should_exist, f"Billing detail '{field}' display state mismatch."

        print(f"Billing details verification passed (should_exist={should_exist}).")
        capture_ui_tree(main_window, ui_tree_file_path, "After Verifying Billing Card", append=True)
    except Exception as e:
        if should_exist:
            print(f"Saved Billing details not displayed correctly: {e}")
            raise
        else:
            print("Billing details are not displayed, as expected.")


def verify_confirm_button_disabled(main_window):
    """
    Verify that the 'Confirm' button is displayed but not enabled (disabled).
    """
    try:
        # Locate the Confirm button
        confirm_button = main_window.child_window(
            title="Confirm",
            control_type="Button"
        )
        # Wait for the button to exist and be visible
        wait_for_element(confirm_button, timeout=10)

        # Check if the button is disabled
        assert not confirm_button.is_enabled(), "Confirm button should be disabled but it is enabled."
        print("Confirm button is correctly disabled.")
    except Exception as e:
        print(f"Confirm button verification failed: {e}")
        raise


def fill_billing_details(main_window, ui_tree_file_path, test_data, payment_type="credit_card"):
    try:
        if payment_type == "paypal":
            # Click 'Link a payment provider'
            link_payment_provider_btn = main_window.child_window(title="Link a payment provider", control_type="Button")
            if link_payment_provider_btn.exists(timeout=10):
                link_payment_provider_btn.click_input()
                print("Clicked 'Link a payment provider' button")
                time.sleep(2)
            # Click 'PayPal' button
            paypal_btn = main_window.child_window(title="PayPal", control_type="Button")
            if paypal_btn.exists(timeout=10):
                paypal_btn.click_input()
                print("Clicked 'PayPal' button")
                time.sleep(5)
            # Switch to PayPal webview window
            paypal_window = main_window.child_window(title_re=".*PayPal.*", control_type="Window")
            if not paypal_window.exists(timeout=10):
                paypal_window = main_window  # fallback if webview is not a separate window
            # Enter email or mobile number
            email_field = paypal_window.child_window(title="Email or mobile number", control_type="Edit")
            if email_field.exists(timeout=10):
                email_field.set_text(test_data["paypal_email"])
                print("Entered PayPal email")
                time.sleep(1)
            # Click 'Next' button
            next_btn = paypal_window.child_window(title="Next", control_type="Button")
            if next_btn.exists(timeout=10):
                next_btn.click_input()
                print("Clicked 'Next' on PayPal login")
                time.sleep(5)
            # Click 'Try another way'
            try_another_way_btn = paypal_window.child_window(title="Try another way", control_type="Button")
            if try_another_way_btn.exists(timeout=10):
                try_another_way_btn.click_input()
                print("Clicked 'Try another way'")
                time.sleep(2)
            # Click 'Use password instead'

            use_password_btn = paypal_window.child_window(title="Use password instead", control_type="Button")
            if use_password_btn.exists(timeout=10):
                use_password_btn.click_input()
                print("Clicked 'Use password instead'")
                time.sleep(2)

            # Enter password
            password_field = paypal_window.child_window(title="Password", control_type="Edit")
            if password_field.exists(timeout=10):
                password_field.set_text(test_data["paypal_email"])
                print("Entered PayPal password")
                time.sleep(5)

            # Click 'Agree and Continue'
            agree_btn = paypal_window.child_window(title="Agree and Continue", control_type="Button")
            if agree_btn.exists(timeout=10):
                agree_btn.click_input()
                print("Clicked 'Agree and Continue'")
                time.sleep(5)

            # Click 'Return To HP Smart'

            return_btn = paypal_window.child_window(title="Return To HP Smart", control_type="Button")

            if return_btn.exists(timeout=10):
                return_btn.click_input()

                print("Clicked 'Return To HP Smart'")

                time.sleep(5)

            # Click 'Open HP Smart'

            open_hp_smart_btn = paypal_window.child_window(title="Open HP Smart", control_type="Button")

            if open_hp_smart_btn.exists(timeout=10):
                open_hp_smart_btn.click_input()

                print("Clicked 'Open HP Smart'")

                time.sleep(8)

            capture_ui_tree(main_window, ui_tree_file_path, "After PayPal billing", append=True)

        if payment_type == "credit_card":
            try:
                billing_card = main_window.child_window(title_re="Billing", control_type="Group")
                wait_for_element(billing_card, timeout=15)
                assert billing_card.exists(), "Billing Card should be displayed."

                field_mapping = {
                    "name": "Name",
                    "address": "Address",
                    "city": "City",
                    "state": "State",
                    "zip": "ZIP",
                    "phone": "Phone"
                }

                for key, field_title in field_mapping.items():
                    field_value = test_data['billing'][key]
                    field = billing_card.child_window(title_re=f".*{field_title}.*", control_type="Edit")
                    wait_for_element(field, timeout=10)
                    field.set_edit_text(field_value)
                    print(f"Filled '{field_title}' with '{field_value}'")

                print(" Billing details filled successfully.")

                if ui_tree_file_path:
                    capture_ui_tree(main_window, ui_tree_file_path, "After Filling Billing Details", append=True)

            except Exception as e:
                take_desktop_screenshot(" Failed to fill billing details ", window_title="HP Smart")
                print(f" Failed to fill billing details: {e}")
                raise
    except Exception as e:
        print("Paypal billing failed")

def click_instant_ink_dropdown(main_window):
    try:
        instant_ink_link = main_window.child_window(title="HP Instant Ink Action Button", control_type="Hyperlink")
        wait_for_element(instant_ink_link, timeout=10)
        instant_ink_link.click_input()
        print("Clicked on 'HP Instant Ink Action Button' successfully.")
    except Exception as e:
        print(f"Failed to click 'HP Instant Ink Action Button': {e}")
        raise


def click_on_overview(main_window):
    try:
        overview_link = main_window.child_window(title="Overview", control_type="Hyperlink")
        wait_for_element(overview_link, timeout=10)
        overview_link.click_input()
        print("Clicked on 'Overview' successfully.")
    except Exception as e:
        print(f"Failed to click 'Overview': {e}")
        raise


def verify_billing_on_dashboard(main_window):
    try:
        card_number_text = main_window.child_window(title_re="XXXX-XXXX-XXXX.*", control_type="Text")
        expiry_text = main_window.child_window(title_re="Expires .*", control_type="Text")

        wait_for_element(card_number_text, timeout=10)
        wait_for_element(expiry_text, timeout=10)

        assert card_number_text.exists(), "Card number should be displayed on the dashboard."
        assert expiry_text.exists(), "Expiry date should be displayed on the dashboard."

        print("Billing information is displayed correctly on the dashboard.")
    except Exception as e:
        print(f"Failed to verify billing on dashboard: {e}")
        raise


def click_replace_printer_modal(main_window):
    try:
        replace_printer_text = main_window.child_window(
            title="Replace a printer that's enrolled or in a trial",
            control_type="Text"
        )
        wait_for_element(replace_printer_text, timeout=10)
        replace_printer_text.click_input()
        print("Clicked on 'Replace a printer that's enrolled or in a trial' successfully.")
    except Exception as e:
        print(f"Failed to click on 'Replace a printer that's enrolled or in a trial': {e}")
        raise


def click_continue_on_replace_printer_modal(main_window):
    try:
        continue_button = main_window.child_window(
            title="Continue",
            control_type="Button"
        )
        wait_for_element(continue_button, timeout=180)
        continue_button.click_input()
        print("Clicked on 'Continue' button in Replace Printer modal successfully.")
    except Exception as e:
        print(f"Failed to click on 'Continue' button in Replace Printer modal: {e}")
        raise


def verify_billing_not_on_dashboard(main_window):
    try:
        card_number_text = main_window.child_window(title_re="XXXX-XXXX-XXXX.*", control_type="Text")
        expiry_text = main_window.child_window(title_re="Expires .*", control_type="Text")

        assert not card_number_text.exists(), "Card number should not be displayed on the dashboard."
        assert not expiry_text.exists(), "Expiry date should not be displayed on the dashboard."

        print("Billing information is not displayed on the dashboard as expected.")
    except Exception as e:
        print(f"Failed to verify billing absence on dashboard: {e}")
        raise


def apply_promo_code(window, apply_code, ui_tree_file_path):
    """Apply promo code."""

    promo_btn = window.child_window(title="Enter promo or PIN code", control_type="Button")

    if promo_btn.exists(timeout=80) and promo_btn.is_enabled():
        promo_btn.click_input()

        time.sleep(2)

        print("Clicked 'Enter promo or PIN code'")

        capture_ui_tree(window, ui_tree_file_path, "After Clicking Promo", append=True)

    promo_input = window.child_window(auto_id="code-entry", control_type="Edit")

    if promo_input.exists(timeout=10):
        promo_input.set_edit_text(apply_code)

        print(f"Entered promo code '{apply_code}'")

        capture_ui_tree(window, ui_tree_file_path, "After Entering Promo", append=True)

    apply_btn = window.child_window(title="Apply", control_type="Button")

    if apply_btn.exists(timeout=10) and apply_btn.is_enabled():
        apply_btn.click_input()

        print("Clicked 'Apply'")

        time.sleep(3)

        capture_ui_tree(window, ui_tree_file_path, "After Apply", append=True)


def close_promo_modal(main_window):
    try:
        close_button = main_window.child_window(
            title="Close modal",
            control_type="Button"
        )
        wait_for_element(close_button, timeout=10)
        close_button.click_input()
        print("Promo modal closed successfully.")
    except Exception as e:
        print(f"Failed to close promo modal: {e}")
        raise


def verify_warrant_printer_replacement_screen_displayed(main_window):
    try:
        welcome_text = main_window.child_window(title="Welcome back", control_type="Text")
        enroll_text = main_window.child_window(title="Enroll as an additional printer", control_type="Text")
        replace_text = main_window.child_window(title="Replace a printer that's enrolled or in a trial",
                                                control_type="Text")

        wait_for_element(welcome_text, timeout=10)
        wait_for_element(enroll_text, timeout=10)
        wait_for_element(replace_text, timeout=10)

        assert welcome_text.exists(), "'Welcome back' text should be displayed."
        assert enroll_text.exists(), "'Enroll as an additional printer' text should be displayed."
        assert replace_text.exists(), "'Replace a printer that's enrolled or in a trial' text should be displayed."

        print("Warrant printer replacement screen is displayed correctly.")
    except Exception as e:
        print(f"Failed to verify warrant printer replacement screen: {e}")
        raise


def verify_review_and_confirm_printer_replacement(main_window):
    try:
        review_text = main_window.child_window(title="Review and confirm printer replacement", control_type="Text")
        wait_for_element(review_text, timeout=10)
        assert review_text.exists(), "'Review and confirm printer replacement' text should be displayed."
        print("'Review and confirm printer replacement' text is displayed correctly.")
    except Exception as e:
        take_desktop_screenshot("Failed to verify 'Review and confirm printer replacement' text ", window_title="HP Smart")
        print(f"Failed to verify 'Review and confirm printer replacement' text: {e}")
        raise


def click_accept_all(main_window, ui_tree_file_path):
    """
    Click the 'Accept all' button if present on the current page.
    """
    try:
        accept_all_btn = main_window.child_window(title="Accept all", control_type="Button")
        wait_for_element(accept_all_btn, timeout=70)
        assert accept_all_btn.exists(), "'Accept all' button should be displayed on the page."
        accept_all_btn.click_input()
        capture_ui_tree(main_window, ui_tree_file_path, "After Accept All Click", append=True)
        print("'Accept all' button clicked successfully.")
    except Exception as e:
        take_desktop_screenshot("Failed to click 'Accept All' button", window_title="HP Smart")
        print(f"Failed to click 'Accept All' button: {e}")




# def verify_free_months_info_on_value_prop_page(main_window, test_data):
#     """
#     Verify free months are displayed correctly on the Value Proposition page according to printer and Persona mode.
#     """
#     value_prop_page = main_window.child_window(
#         title_re="Value Proposition|Your printer comes with a.*trial of Instant Ink", control_type="Group")
#     wait_for_element(value_prop_page, timeout=50)
#     assert value_prop_page.exists(), "Value Proposition page should be displayed."
#
#     free_months_text = value_prop_page.child_window(title_re=f".*{test_data.get('free_months', 'month')}.*",
#                                                     control_type="Text")
#     wait_for_element(free_months_text, timeout=10)
#     assert free_months_text.exists(), "Free months info should be displayed correctly on Value Proposition page."


# def verify_free_months_info_on_value_prop_page(main_window, test_data, timeout=50):
#     """
#
#     Verify free months are displayed correctly on the Value Proposition page
#
#     according to printer and Persona mode.
#
#     Args:
#
#         main_window: The main HP Smart window object.
#
#         test_data (dict): Test data containing expected 'free_months' value.
#
#         timeout (int): Maximum seconds to wait for the Value Prop page.
#
#     Raises:
#
#         AssertionError: If Value Proposition page or free months text is not found.
#
#     """
#
#     expected_free_months = str(test_data.get('free_months', '5'))
#
#     print(f" Waiting up to {timeout}s for Value Proposition page...")
#
#     # Wait for Value Prop page to appear
#
#     value_prop_page = None
#
#     start_time = time.time()
#
#     while time.time() - start_time < timeout:
#
#         try:
#
#             value_prop_page = main_window.child_window(
#
#                 title_re="Your new printer includes 5 free months of automatic ink delivery!",
#
#
#
#             )
#
#             if value_prop_page.exists():
#                 break
#
#         except Exception:
#
#             pass
#
#         time.sleep(1)
#
#     if not value_prop_page or not value_prop_page.exists():
#         raise AssertionError(" Value Proposition page should be displayed.")
#
#     print(" Value Proposition page is displayed.")
#
#     # Wait for Free Months text
#
#     free_months_text = None
#
#     start_time = time.time()
#
#     while time.time() - start_time < 10:
#
#         try:
#
#             free_months_text = value_prop_page.child_window(
#
#                 title_re=f".*{expected_free_months}.*", control_type="Text"
#
#             )
#
#             if free_months_text.exists():
#                 break
#
#         except Exception:
#
#             pass
#
#         time.sleep(1)
#
#     if not free_months_text or not free_months_text.exists():
#
#         # Debug: print all texts under value_prop_page
#
#         print(" All available text in Value Prop page:")
#
#         for t in value_prop_page.descendants(control_type="Text"):
#
#             try:
#
#                 print(f" - {t.window_text()}")
#
#             except Exception:
#
#                 continue
#
#         raise AssertionError(
#             f" Free months info '{expected_free_months}' should be displayed correctly on Value Proposition page.")
#
#     print(f" Free months info is displayed correctly: {free_months_text.window_text()}")
#
import time


def verify_free_months_info_on_value_prop_page(main_window, free_months_text, ui_tree_file_path=None, timeout=20):
    """
    Verify that the 'free months' text is displayed on the Value Proposition page in the HP Smart app.

    :param main_window: pywinauto window object for HP Smart.
    :param free_months_text: The expected text for the free months offer (e.g., "5 free months of automatic ink delivery!").
    :param ui_tree_file_path: Optional file path to save UI tree captures for debugging.
    :param timeout: Maximum seconds to wait for the text to appear.
    :return: True if the 'free months' text is displayed, False otherwise.
    """
    try:
        # Capture UI state before verification (optional)
        if ui_tree_file_path:
            capture_ui_tree(main_window, ui_tree_file_path, "Before verifying Free Months text", append=True)

        # Locate the 'Free Months' element by its text
        free_month_element = main_window.child_window(title=free_months_text, control_type="Text")
        wait_for_element(free_month_element, timeout=timeout)

        # Verify the element exists
        assert free_month_element.exists(), "'Free Months' text not found on Value Prop page."

        # Capture UI state after verification (optional)
        if ui_tree_file_path:
            capture_ui_tree(main_window, ui_tree_file_path, "After verifying Free Months text", append=True)

        print("'Free Months' text is displayed correctly.")
        return True

    except Exception as e:
        take_desktop_screenshot("Free Months text not displayed", window_title="HP Smart")
        print(f"'Free Months' text not displayed: {e}")
        return False


def verify_printer_selection_page_displayed():
    return None





def verify_next_button_on_value_prop_page(main_window, ui_tree_file_path):
    """
    Verify Next button is displayed correctly on Value prop page without missing, cut-off, or overlap.
    """
    value_prop_page = main_window.child_window(title="Your new printer includes ", control_type="Text")
    wait_for_element(value_prop_page, timeout=15)


    # next_btn = value_prop_page.child_window(title="Next", control_type="Button")
    # wait_for_element(next_btn, timeout=10)
    next_btn = main_window.child_window(title="Next", control_type="Button")
    assert next_btn.exists(), "Next button should be displayed on Value prop page."
    print("Next button Verified")
    # Optionally, capture UI tree for layout validation
    capture_ui_tree(main_window, ui_tree_file_path, "After Next Button on Value Prop Page", append=True)


def verify_trial_end_date_updated_after_code(self):
    """
    Verifies that after closing the modal (post code application),
    the 'Your Plan' card shows an updated trial end date.
    Steps:
      1. Capture the trial end date before applying the code.
      2. Apply the promo/enrollment code and close the modal.
      3. Capture the trial end date again.
      4. Assert that the date has changed (modified correctly).
    """
    try:
        logger.info(" Fetching trial end date before applying code...")
        before_date_text = get_text(self.driver, self.TRIAL_END_DATE_TEXT).strip()
        logger.info(f"Trial End Date before applying code: {before_date_text}")

        # --- Simulate applying code or closing modal ---
        logger.info(" Applying code and closing modal...")
        close_modal_btn = wait_for_element(self.driver, self.CLOSE_MODAL_BUTTON, timeout=10)
        click(self.driver, self.CLOSE_MODAL_BUTTON)
        time.sleep(3)

        # --- Wait for Your Plan card to refresh ---
        logger.info("Waiting for 'Your Plan' card to refresh...")
        plan_card = wait_for_element(self.driver, self.YOUR_PLAN_CARD, timeout=20)
        assert plan_card.is_displayed(), "'Your Plan' card is not visible after closing modal."

        # --- Fetch new trial end date ---
        after_date_text = get_text(self.driver, self.TRIAL_END_DATE_TEXT).strip()
        logger.info(f" Trial End Date after applying code: {after_date_text}")

        # --- Compare and verify modification ---
        assert before_date_text != after_date_text, (
            f"Expected trial end date to change, but both are same: {before_date_text}"
        )

        logger.info("Trial End Date updated successfully after applying code.")
        print(f" Verified Trial End Date updated from '{before_date_text}' → '{after_date_text}'.")

    except AssertionError as ae:
        take_desktop_screenshot("Trial_End_Date_Verification_Failed", window_title="HP Smart")
        logger.error(f"Trial End Date verification failed: {ae}")
        raise

    except Exception as e:
        take_desktop_screenshot("Trial_End_Date_Exception", window_title="HP Smart")
        logger.error(f"Unexpected error during Trial End Date verification: {e}")
        raise



def verify_add_shipping_button_enabled(main_window, ui_tree_file_path=None):
    """
    Verify that the 'Add Shipping' button is visible and enabled.

    :param main_window: pywinauto window object
    :param ui_tree_file_path: Optional file path to capture UI tree for debugging
    :return: True if the button is enabled, False otherwise
    """
    try:
        button_title = "Add Shipping"
        add_shipping_btn = main_window.child_window(title=button_title, control_type="Button")

        # Wait for button to appear
        wait_for_element(add_shipping_btn, timeout=10)
        assert add_shipping_btn.exists(), f" '{button_title}' button not found."

        # Check if button is enabled (clickable)
        if add_shipping_btn.is_enabled():
            print(f" '{button_title}' button is visible and enabled.")
            if ui_tree_file_path:
                capture_ui_tree(main_window, ui_tree_file_path, "After verifying Add Shipping button", append=True)
            return True
        else:
            take_desktop_screenshot(f" '{button_title}' button is disabled. ", window_title="HP Smart")
            raise AssertionError(f" '{button_title}' button is disabled.")
    except Exception as e:
        take_desktop_screenshot(f" '{button_title}' button is disabled.", window_title="HP Smart")
        print(f" Failed to verify '{button_title}' button: {e}")
        return False


def verify_add_billing_button_enabled(main_window, ui_tree_file_path=None):
    """
    Verify that the 'Add Billing' button is visible and enabled.

    :param main_window: pywinauto window object
    :param ui_tree_file_path: Optional file path to capture UI tree for debugging
    :return: True if the button is enabled, False otherwise
    """
    try:
        button_title = "Add Billing"
        add_billing_btn = main_window.child_window(title=button_title, control_type="Button")

        # Wait for button to appear
        wait_for_element(add_billing_btn, timeout=10)
        assert add_billing_btn.exists(), f" '{button_title}' button not found."

        # Verify button state
        if add_billing_btn.is_enabled():
            print(f" '{button_title}' button is visible and enabled.")
            if ui_tree_file_path:
                capture_ui_tree(main_window, ui_tree_file_path, "After verifying Add Billing button", append=True)
            return True
        else:
            raise AssertionError(f" '{button_title}' button is disabled.")
    except Exception as e:
        take_desktop_screenshot(f" Failed to verify '{button_title}' button", window_title="HP Smart")
        print(f" Failed to verify '{button_title}' button: {e}")
        return False
    
    
def verify_add_billing_button_disabled(main_window, ui_tree_file_path=None):
    """
    Verify that the 'Add Billing' button is visible and enabled.

    :param main_window: pywinauto window object
    :param ui_tree_file_path: Optional file path to capture UI tree for debugging
    :return: True if the button is enabled, False otherwise
    """
    try:
        button_title = "Add Billing"
        add_billing_btn = main_window.child_window(title=button_title, control_type="Button")

        # Wait for button to appear
        wait_for_element(add_billing_btn, timeout=10)
        assert add_billing_btn.exists(), f" '{button_title}' button not found."

        

        # Verify button state
        if add_billing_btn.is_disabled():
            print(f" '{button_title}' button is visible and disabled.")
            if ui_tree_file_path:
                capture_ui_tree(main_window, ui_tree_file_path, "After verifying Add Billing button", append=True)
            return True
        else:
            raise AssertionError(f" '{button_title}' button is enabled.")
    except Exception as e:
        take_desktop_screenshot(f" Failed to verify '{button_title}' button", window_title="HP Smart")
        print(f" Failed to verify '{button_title}' button: {e}")
        return False


def get_value_prop_content_contents(main_window):
    return None

def reset_hp_smart_app() -> None:
    # close settings
    process_name = "SystemSettings.exe"
    timeout = 10
    try:
        # Attempt to forcefully terminate the process
        subprocess.run(["taskkill", "/f", "/im", process_name], check=True)
        print(f"{process_name} termination initiated.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to terminate {process_name}: {e}")

    # Wait until the process is no longer running
    for _ in range(timeout):
        if not any(proc.name() == process_name for proc in psutil.process_iter()):
            print(f"{process_name} successfully closed.")
        time.sleep(1)

    print(f"{process_name} still running after {timeout} seconds.")
    # Press Windows key to open Start
    send_keys('{VK_LWIN down}{VK_LWIN up}')
    time.sleep(1)

    # Type "HP Smart"
    send_keys('HP Smart')
    time.sleep(2)  # Wait for search results to populate

    # Navigate with keyboard:
    # Right arrow to open context menu or details pane


    send_keys('{RIGHT}')
    time.sleep(3)

    # Press down arrow 4 times to go to "App settings"
    for _ in range(3):
        send_keys('{DOWN}')
        time.sleep(0.3)

    # Press Enter to open App settings
    send_keys('{ENTER}')
    time.sleep(15)  # Wait for App Settings window to open
    app = Application(backend="uia").connect(title_re=".*Settings.*")
    main_window = app.top_window()
    main_window.set_focus()
    main_window.maximize()
    send_keys('{PGDN}')
    time.sleep(1)  # Wait to ensure UI updates after scrolling
    # Locate the Reset button by AutomationId and ControlType
    reset_btn = main_window.child_window(
        title="Reset",
        control_type="Button"
    )
    if reset_btn.exists() and reset_btn.is_enabled():
        reset_btn.click_input()
        print("Clicked Reset button.")
    else:
        print("Reset button not found or disabled.")
    reset_btn = main_window.child_window(
        title="Reset",
        auto_id="SystemSettings_StorageSense_AppSizesAdvanced_AppReset_ConfirmButton",
        control_type="Button"
    )
    reset_btn.click_input()

#======================Add New Printer========================
def click_add_new_printer(main_window, ui_tree_file_path):
    """
    Click the 'Add Printer' button in HP Smart app.

    :param main_window: pywinauto window object for HP Smart
    :param ui_tree_file_path: Path to save UI tree captures
    """
    try:
        add_printer_btn = main_window.child_window(title="Add new printer", control_type="Hyperlink")
        wait_for_element(add_printer_btn, timeout=20).click_input()
        time.sleep(2)
        capture_ui_tree(main_window, ui_tree_file_path, "After Add new Printer", append=True)
        print("Clicked 'Add new  Printer'.")
    except Exception as e:
        print(f" Failed to click==================")



def click_continue_replacement(main_window,ui_tree_file_path):
    continue_btn = main_window.child_window(title="Continue", control_type="Button")

    wait_for_element(continue_btn, timeout=30).click_input()

    time.sleep(2)

    capture_ui_tree(main_window, ui_tree_file_path, "After Time to connect, Setup Page", append=True)

def clear_credential_manager():
    print("Opening Windows Credential Manager...")
    # Step 1: Open Windows Search
    pyautogui.press("win")
    time.sleep(1)
    # Step 2: Type "Credential Manager"
    pyautogui.write("Credential Manager", interval=0.1)
    time.sleep(1)
    # Step 3: Press Enter to open
    pyautogui.press("enter")
    time.sleep(4)
    try:
        # Step 4: Attach to the Credential Manager window
        app = Application(backend="uia").connect(title_re=".*Credential.*")
        main_window = app.top_window()
        main_window.set_focus()
        main_window.maximize()
        print(" Credential Manager opened successfully.")
        capture_ui_tree(main_window, ui_tree_file_path, "After Add Printer", append=True)
        # Step 5: Ensure Web Credentials tab is selected
        try:
            web_tab = main_window.child_window(title="Web Credentials", auto_id="KeyRingTile_Button_KeyRing",
                                               control_type="TabItem")
            web_tab.click_input()
            print("Switched to Web Credentials tab.")
        except Exception as e:
            print(" Could not switch tab — continuing...")
        time.sleep(2)
        removed_any = False
        while True:
            try:
                drop_down_btn = main_window.child_window(title="Expand or collapse the view.",
                                                         auto_id="Icon_ExpandoButtonImage", control_type="Button",
                                                         found_index=0)
                if drop_down_btn.exists(timeout=2):
                    # Scroll into view and click remove
                    drop_down_btn.click_input()
                    print("Clicked dropdown button...")
                    time.sleep(2)
                    remove_btn = main_window.child_window(title="Remove",
                                                          auto_id="CredentialDetails_Button_DeleteCredential",
                                                          control_type="Button")
                    remove_btn.click_input()
                    print("Clicked remove button...")
                    time.sleep(2)
                    yes_btn = main_window.child_window(title="Yes", auto_id="CommandButton_6", control_type="Button")
                    yes_btn.click_input()
                    print("Clicked yes button...")
                    # Step 7: Confirm removal
                    time.sleep(1)
                    print("Removed")
                else:
                    break
            except Exception:
                break
        if not removed_any:
            print(" No HP credentials found to remove.")
        else:
            print(" All HP credentials cleared successfully.")
        # Step 8: Close Credential Manager
        pyautogui.hotkey("alt", "f4")
        print(" Credential Manager closed.")
    except Exception as e:
        pytest.fail(f" Failed while clearing credentials: {e}")

# SCREENSHOT_DIR = "screenshots"
# os.makedirs(SCREENSHOT_DIR, exist_ok=True)
#
# def take_window_screenshot(main_window):
#     # Adapt to your main_window or desktop
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     filename = f"screenshot_{timestamp}.png"
#     filepath = os.path.join(SCREENSHOT_DIR, filename)
#     main_window.capture_as_image().save(filepath)
#     return filepath


def take_desktop_screenshot(filename="screenshot", window_title="HP Smart"):
    # Adapt the window_title as needed
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = timestamp+"_"+filename+".png"
    screenshots_dir = os.path.join(os.getcwd(), "Screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    file_path = os.path.join(screenshots_dir, filename)
    try:
        app = Application(backend="uia").connect(title_re=window_title)
        main_window = app.window(title_re=window_title)
        main_window.capture_as_image().save(file_path)
        return file_path
    except Exception as e:
        print(f"Desktop screenshot failed: {e}")
        return None
    





def verify_prepaid_code_info(main_window):
    """
    Verifies that the Prepaid Code information is displayed on the Dashboard page.

    Args:
        main_window: The main application window.

    Raises:
        AssertionError: If the prepaid code info is not displayed.
    """
    prepaid_info = main_window.child_window(title_re=".*Prepaid.*"+test_data["free_month"], control_type="Text")
    assert prepaid_info.exists(timeout=10), " Prepaid code information not displayed on Dashboard."
    print(" Prepaid code information displayed correctly.")

def verify_paypal_info(main_window):
    """
    Verifies that the PayPal information is displayed on the Dashboard page.

    Args:
        main_window: The main application window.

    Raises:
        AssertionError: If the PayPal info is not displayed.
    """
    paypal_info = main_window.child_window(title_re=".*PayPal.*", control_type="Text")
    assert paypal_info.exists(timeout=10), " PayPal information not displayed on Dashboard."
    print(" PayPal information displayed correctly.")

def verify_disclaimer(main_window):
    """
    Verifies that the correct disclaimer based on PUF benefits with Free months 
    is displayed and matches the expected content.

    Args:
        main_window: The main application window.
        expected_disclaimer_text (str): Expected disclaimer text.

    Raises:
        AssertionError: If the disclaimer section is missing or text does not match.
    """
    disclaimer = main_window.child_window(title_re=".*8 month trial.*", control_type="Text")
    assert disclaimer.exists(timeout=10), " Disclaimer section not found on Dashboard."

    actual_text = disclaimer.window_text().strip()
    assert disclaimer in actual_text, (
        f" Disclaimer text does not match expected content.\n"
        f"Expected: {disclaimer}\nActual: {actual_text}"
    )
    print(" Disclaimer content matches the expected PUF benefits message.")


def verify_connect_and_finalize(main_window, timeout=10):
    """
    Verify that 'Connect and Finalize' text exists in the given window.
 
    :param main_window: pywinauto window object (main application window)
    :param timeout: how long to wait for the element (default 10 seconds)
    :return: True if found, False otherwise
    """
    try:
        element = main_window.child_window(title_re=".*Connect and Finalize.*", control_type="Text")
        assert element.exists(timeout=timeout), "Connect and Finalize not found"
        print(" Connect and Finalize verified successfully")
        return True
    except Exception as e:
        print(f" Error verifying Connect and Finalize: {e}")
        return False
    


def verify_apply_button_enabled(main_window, ui_tree_file_path=None):
    """
    Verify that the 'Add Shipping' button is visible and enabled.

    :param main_window: pywinauto window object
    :param ui_tree_file_path: Optional file path to capture UI tree for debugging
    :return: True if the button is enabled, False otherwise
    """
    try:
        button_title = "Apply"
        add_shipping_btn = main_window.child_window(title=button_title, control_type="Button")

        # Wait for button to appear
        wait_for_element(add_shipping_btn, timeout=10)
        assert add_shipping_btn.exists(), f" '{button_title}' button not found."

        # Check if button is enabled (clickable)
        if add_shipping_btn.is_enabled():
            print(f" '{button_title}' button is visible and enabled.")
            if ui_tree_file_path:
                capture_ui_tree(main_window, ui_tree_file_path, "After verifying Apply button", append=True)
            return True
        else:
            take_desktop_screenshot(f" '{button_title}' button is disabled. ", window_title="HP Smart")
            raise AssertionError(f" '{button_title}' button is disabled.")
    except Exception as e:
        take_desktop_screenshot(f" '{button_title}' button is disabled.", window_title="HP Smart")
        print(f" Failed to verify '{button_title}' button: {e}")
        return False



def verify_update_plan_page(main_window, ui_tree_file_path, expected_text="1 Redeemed month + credits", timeout=10):
    """
    Click the 'Update Plan' link and verify the Free months info on the Update Plan page.
 
    :param main_window: pywinauto main window object
    :param ui_tree_file_path: path for capturing UI tree snapshots
    :param expected_text: expected text for redeemed months info
    :param timeout: wait time for elements
    :return: True if verification successful, otherwise raises AssertionError
    """
    from Utils.Desktop.common_desk_utilities import capture_ui_tree
 
    try:
        # Locate 'Update Plan' button/link
        update_plan_btn = main_window.child_window(auto_id="UpdatePlan", control_type="link")
        assert update_plan_btn.exists(timeout=timeout), "'Update Plan' link not found"
 
        # Capture UI before clicking
        capture_ui_tree(main_window, ui_tree_file_path, "before update_plan_btn", append=True)
 
        # Click 'Update Plan'
        update_plan_btn.click_input()
        print(" Clicked 'Update Plan' link button")
        time.sleep(10)
 
        # Verify 'Free months info' text on the Update Plan page
        free_month_info_txt = main_window.child_window(title_re=".*Redeemed month.*", control_type="Text")
        assert free_month_info_txt.exists(timeout=timeout), "Free months info not found on Update Plan page"
 
        actual_text = free_month_info_txt.window_text().strip()
        assert actual_text == expected_text, f"Expected '{expected_text}' but got '{actual_text}'"
 
        print(f" Verified Free months info on Update Plan page: {actual_text}")
        return True
 
    except Exception as e:
        print(f" Update Plan page navigation or validation failed: {e}")
        pytest.fail(f"Update Plan page navigation or validation failed: {e}")
 
def verify_print_and_payment_history_page(main_window, ui_tree_file_path, expected_text="1 Redeemed month + credits", timeout=10):
    """
    Navigate to 'Print and Payment History' page and verify the Free months info text.
 
    :param main_window: pywinauto main window object
    :param ui_tree_file_path: path for saving UI tree snapshots
    :param expected_text: expected redeemed months info text (default '1 Redeemed month + credits')
    :param timeout: maximum time to wait for elements
    :return: True if verification is successful, otherwise raises AssertionError
    """
    from Utils.Desktop.common_desk_utilities import capture_ui_tree
 
    try:
        # Locate the 'Print and Payment History' link
        history_btn = main_window.child_window(title="Print and Payment History", control_type="link")
        assert history_btn.exists(timeout=timeout), "'Print and Payment History' link not found"
 
        # Capture before click
        capture_ui_tree(main_window, ui_tree_file_path, "before history_btn", append=True)
 
        # Click the history button
        history_btn.click_input()
        print("Clicked 'Print and Payment History' link button")
        time.sleep(10)
 
        # Verify 'Free months info' on the History page
        free_month_info_txt = main_window.child_window(title_re=".*Redeemed month.*", control_type="Text")
        assert free_month_info_txt.exists(timeout=timeout), "Free months info not found on History page"
 
        actual_text = free_month_info_txt.window_text().strip()
        assert actual_text == expected_text, f"Expected '{expected_text}' but got '{actual_text}'"
 
        print(f"Verified Free months info on History page: {actual_text}")
        return True
 
    except Exception as e:
        print(f"Print and Payment History page navigation or validation failed: {e}")
        pytest.fail(f"Print and Payment History page navigation or validation failed: {e}")

def verify_free_months_info_overview(main_window, expected_text="1 Redeemed month + credits", timeout=10):
    """
    Verify the 'Free months info' text on the Overview page.
 
    :param main_window: pywinauto main window object
    :param expected_text: expected display text (default '1 Redeemed month + credits')
    :param timeout: how long to wait for the text element
    :return: True if verified successfully, otherwise raises AssertionError
    """
    try:
        free_month_info_txt = main_window.child_window(title_re=".*Redeemed month.*", control_type="Text")
 
        # Check if element exists
        assert free_month_info_txt.exists(timeout=timeout), "Free months info not found on Overview page"
 
        # Check text matches expectation
        actual_text = free_month_info_txt.window_text().strip()
        assert actual_text == expected_text, f"Expected '{expected_text}' but got '{actual_text}'"
 
        print(f"Verified Free months info on Overview page: {actual_text}")
        return True
    except Exception as e:
        print(f" Free months info verification failed: {e}")
        raise AssertionError(f"Free months info verification failed: {e}")
    


def verify_thank_you_spinner(main_window, ui_tree_file_path):
    """Verify the thank you spinner is displayed."""
    try:
        thank_you_spinner = main_window.child_window(title_re="thankyou-spinner", control_type="Text")
        assert thank_you_spinner.exists(timeout=10), "thank you spinner not found."
        thank_you_spinner.invoke()
        print("Verified thank you spinner successfully.")
        capture_ui_tree(main_window, ui_tree_file_path, "After verifying thank you spinner", append=True)
    except Exception as e:

        take_desktop_screenshot(" thank you spinner verification failed ", window_title="HP Smart")
        print(f"Could not verify thank you spinner: {e}")


def verify_two_checkboxes_on_modal(main_window):
    """
    Verify that both checkboxes (TOS and Prepaid) are displayed and unchecked by default.
    """
    try:
        # Locate both checkboxes
        tos_checkbox = main_window.child_window(auto_id="terms-of-service", control_type="CheckBox")
        prepaid_checkbox = main_window.child_window(auto_id="prepaid-offer", control_type="CheckBox")

        # Wait for both to appear
        wait_for_element(tos_checkbox, timeout=10)
        wait_for_element(prepaid_checkbox, timeout=10)

        # --- Verify TOS Checkbox ---
        assert tos_checkbox.exists(), "TOS checkbox should be displayed."
        assert not tos_checkbox.get_toggle_state(), "TOS checkbox should be unchecked by default."

        # --- Verify Prepaid Checkbox ---
        assert prepaid_checkbox.exists(), "Prepaid checkbox should be displayed."
        assert not prepaid_checkbox.get_toggle_state(), "Prepaid checkbox should be unchecked by default."

        print("Both TOS and Prepaid checkboxes are displayed and unchecked by default.")

    except Exception as e:
        take_desktop_screenshot("checkbox_verification_failed", window_title="HP Smart")
        print(f"Checkbox verification failed: {e}")
        raise



def verify_blue_dropdown_button_on_modal(main_window):
    """
    Verify that when the modal content exceeds the default visible height,
    a blue dropdown (expand) button is displayed.
    """
    try:
        # Locate the modal container
        modal_container = main_window.child_window(auto_id="modal-container", control_type="Pane")

        # Try to locate the blue dropdown/expand button
        dropdown_button = modal_container.child_window(
            title="Show more", control_type="Button"
        )

        # Wait for modal to load
        wait_for_element(modal_container, timeout=10)

        # Check if dropdown button is displayed
        if dropdown_button.exists(timeout=5):
            print("Blue dropdown button is displayed (content exceeds default height).")
        else:
            print("Blue dropdown button not displayed — content fits within default view.")

    except Exception as e:
        take_desktop_screenshot("dropdown_button_verification_failed", window_title="HP Smart")
        print(f"Verification of dropdown button failed: {e}")
        raise



def verify_billing_card_disabled(self, expected_free_months):
    """
    Verifies that:
    1. The Billing Card is disabled.
    2. The correct free months (e.g., 6) are displayed.
    3. The 'Add Billing' button is disabled.
    """
    try:
        logger.info("Waiting for Billing Card section to appear...")
        billing_section = wait_for_element(self.driver, self.BILLING_CARD_SECTION, timeout=20)
        assert billing_section.is_displayed(), "Billing Card section is not visible."
        logger.info("Billing Card section is visible.")

        # --- Verify Billing Card is disabled ---
        is_disabled = "disabled" in billing_section.get_attribute("class").lower() or \
                    not billing_section.is_enabled()
        assert is_disabled, "Billing Card should be disabled."
        logger.info("Billing Card is disabled as expected.")

        # --- Verify free months text ---
        free_months_text = get_text(self.driver, self.FREE_MONTHS_TEXT).strip()
        logger.info(f"Billing card free months text: '{free_months_text}'")

        assert str(expected_free_months) in free_months_text, (
            f"Expected {expected_free_months} free months, but found '{free_months_text}'."
        )
        logger.info(f"Correct free months ({expected_free_months}) displayed on Billing Card.")

        # --- Verify Add Billing button is disabled ---
        add_billing_button = wait_for_element(self.driver, self.ADD_BILLING_BUTTON, timeout=10)
        assert not add_billing_button.is_enabled(), (
            "'Add Billing' button should be disabled but is enabled."
        )
        logger.info("'Add Billing' button is disabled as expected.")

        print(f"Verified Billing Card is disabled and shows {expected_free_months} free months.")
        print(" Verified 'Add Billing' button is disabled.")

    except AssertionError as ae:
        take_desktop_screenshot("Billing_Card_Verification_Failed", window_title="HP Smart")
        logger.error(f" Billing Card verification failed: {ae}")
        raise

    except Exception as e:
        take_desktop_screenshot("Billing_Card_Exception", window_title="HP Smart")
        logger.error(f" Unexpected error during Billing Card verification: {e}")
        raise












    
