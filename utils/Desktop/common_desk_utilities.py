import subprocess
import psutil
import time
import logging

import time
import pytest
import logging
from Utils.Desktop.hp_smart_utils import take_desktop_screenshot, wait_for_element
from pywinauto.findwindows import ElementNotFoundError


# Close the application
def close_hp_smart_app(main_window_spec):
    try:
        main_window_spec.close()
        print("HP Smart application closed successfully.")
    except Exception as e:
        print(f"Failed to close HP Smart application: {e}")


# Close the application by killing process
def force_close_hp_smart(process_name="HP.Smart.exe", timeout=10):
    try:
        # Attempt to forcefully terminate the process
        subprocess.run(["taskkill", "/f", "/im", process_name], check=True)
        print(f"{process_name} termination initiated.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to terminate {process_name}: {e}")
        return False

    # Wait until the process is no longer running
    for _ in range(timeout):
        if not any(proc.name() == process_name for proc in psutil.process_iter()):
            print(f"{process_name} successfully closed.")
            return True
        time.sleep(1)

    print(f"{process_name} still running after {timeout} seconds.")
    return False


# Capture UI tree to find locators
def capture_ui_tree(control_spec, file_path, section_title=None, append=True):
    """
    Captures the UI tree of a given control and writes it to a file.

    Args:
        control_spec: pywinauto control specification (e.g., window or pane).
        file_path: Full path to the output file.
        section_title: Optional title to separate sections in the file.
        append: If True, appends to the file; otherwise, overwrites.
    """
    import io, sys,os
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        buffer = io.StringIO()
        sys_stdout_backup = sys.stdout
        sys.stdout = buffer
        control_spec.print_control_identifiers()
        sys.stdout = sys_stdout_backup
        ui_tree = buffer.getvalue()
        buffer.close()

        mode = "a" if append else "w"
        with open(file_path, mode, encoding="utf-8") as f:
            if section_title:
                f.write(f"\n\n--- {section_title} ---\n")
            f.write(ui_tree)
        print(f"UI tree captured for: {section_title or 'Unnamed Section'}")
    except Exception as e:
        sys.stdout = sys_stdout_backup
        raise RuntimeError(f"Failed to capture UI tree: {e}")


def launch_hp_smart_app():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    max_retries = 1
    max_wait = 100
    check_interval = 5

    for attempt in range(max_retries + 1):
        logging.info(f"Attempt {attempt + 1} to launch HPSMart app.")

        # Launch HP app using PowerShell
        try:
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Start-Process HPPrinterControl:AD2F1837.HPPrinterControl_v10z8vjag6ke6",
                ],
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            logging.warning("Launch command timed out.")

        start_time = time.time()
        loading = True

        while loading and (time.time() - start_time) < max_wait:
            # Simulate loading check
            logging.info(
                f"Attempt {attempt+1}: App is still loading... ({int(time.time() - start_time)}s elapsed)"
            )
            time.sleep(check_interval)

            # Simulate successful load
            loading = False
            logging.info(
                f"App loaded successfully after {int(time.time() - start_time)} seconds on attempt {attempt+1}."
            )
            break

        if not loading:
            break

        logging.warning(
            f"App stuck in loading for more than {max_wait} seconds on attempt {attempt+1}. Killing HP.myHP process."
        )

        if attempt == max_retries:
            raise Exception(
                "App stuck in loading after retries. HP.myHP process killed."
            )


def take_screenshot(window_spec, filename="desktop_screenshot.png"):
    """
    Takes a screenshot of the given window and saves it to the Screenshots folder.

    Args:
        window_spec: pywinauto window specification object.
        filename: Name of the screenshot file.
    """
    import os
    # screenshots_dir = os.path.join(
    #     os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    #     "Screenshots"
    # )
    screenshots_dir = os.path.join(os.getcwd(), "Screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    filepath = os.path.join(screenshots_dir, filename)

    # os.makedirs(screenshots_dir, exist_ok=True)
    # filepath = os.path.join(screenshots_dir, filename)
    #filepath="C:\\Users\hpx\Downloads\Instant_Ink_git\InstantInk_QE_Automation\Screenshots"
    try:
        image = window_spec.capture_as_image()
        image.save(filepath)
        print(f"Screenshot saved: {filepath}")
        return filepath
    except Exception as e:
        print(f"Failed to take screenshot: {e}")
        return None
    



logger = logging.getLogger(__name__)

def select_printer_from_list_(main_window, ui_tree_file_path, test_data):
    """
    Selects the first available printer in beaconing mode from the test data.
    It skips printers that are offline or already added.

    :param main_window: pywinauto window object for HP Smart
    :param ui_tree_file_path: Path to save UI tree captures
    :param test_data: Dictionary containing printer names (printer1, printer2, printer3, ...)
    """

    try:
        printers = [v for k, v in test_data.items() if "printer" in k.lower()]
        beaconing_list = main_window.child_window(
            title="BeaconingPrinters", auto_id="BeaconingGridView", control_type="List"
        )

        for printer_name in printers:
            logger.info(f"Checking printer availability: {printer_name}")
            print(f"Checking printer availability: {printer_name}")

            try:
                printer_item = beaconing_list.child_window(
                    title_re=f"DEVICEVIEWMODEL:{printer_name}", control_type="ListItem"
                )

                # Wait until it appears (if it doesn’t, move to next)
                wait_for_element(printer_item, timeout=15)

                # Verify it is not offline or already added
                printer_text = printer_item.window_text()
                if "Offline" in printer_text or "IP" in printer_text:
                    logger.warning(f"Printer '{printer_name}' is not available (status: {printer_text}). Skipping.")
                    print(f"Printer '{printer_name}' is not available (status: {printer_text}). Skipping.")
                    continue

                # If it reaches here, printer is beaconing and ready
                printer_item.click_input()
                time.sleep(3)
                capture_ui_tree(main_window, ui_tree_file_path, f"Selected Printer: {printer_name}", append=True)
                print(f" Successfully selected beaconing printer: {printer_name}")
                logger.info(f" Successfully selected beaconing printer: {printer_name}")
                return printer_name

            except ElementNotFoundError:
                logger.warning(f"Printer '{printer_name}' not found in beaconing list. Trying next...")
                print(f"Printer '{printer_name}' not found in beaconing list. Trying next...")
                continue
            except Exception as e:
                logger.error(f"Error checking printer '{printer_name}': {e}")
                print(f"Error checking printer '{printer_name}': {e}")
                continue

        # If no beaconing printer found
        take_desktop_screenshot("No beaconing printer available", window_title="HP Smart")
        pytest.fail(" No available beaconing printers found in the provided test data.")

    except Exception as e:
        logger.exception("Failed during beaconing printer selection.")
        take_desktop_screenshot("Failed beaconing printer selection", window_title="HP Smart")
        pytest.fail(f"Failed to select any beaconing printer: {e}")
