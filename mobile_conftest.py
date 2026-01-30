"""
Mobile-specific pytest configuration and fixtures
Separate from main conftest.py to avoid import issues
"""

import logging
import os
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)


def load_mobile_test_data() -> Dict[str, Any]:
    """Load mobile test data from JSON file"""
    try:
        # Get the directory where this file is located (root level)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_file = os.path.join(current_dir, "TestData", "mobile_test_data.json")
        with open(test_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Mobile test data loaded from: {test_data_file}")
        return data
    except FileNotFoundError:
        logger.error(f"Test data file not found: {test_data_file}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in test data file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading test data: {e}")
        raise


def load_valid_credentials() -> Dict[str, str]:
    """Load valid test user credentials"""
    data = load_mobile_test_data()
    users = data.get("test_users", {})
    return {
        "email": users.get("valid_email", ""),
        "password": users.get("valid_password", ""),
        "printer_ip":users.get("printer_ip",""),
        "printer_ip_replace":users.get("printer_ip_replace",""),
        "printer_pin":users.get("printer_pin",""),
        "printer_pin_replace":users.get("printer_pin_replace","")
    }
