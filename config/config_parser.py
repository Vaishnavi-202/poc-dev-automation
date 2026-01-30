# import json
# import os

# def load_config():
#     config_path = os.path.join(os.path.dirname(__file__), 'Config.json')
#     with open(config_path, 'r') as f:
#         return json.load(f)


import json
import os
import sys

def load_config():
    # Load base config
    config_path = os.path.join(os.path.dirname(__file__), 'Config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)

    # CLI overrides
    cli_args = sys.argv

    # Browser override
    for arg in cli_args:
        if arg.startswith("--browserName="):
            config["browserName"] = arg.split("=")[1].lower()

    # Headless override via --headedMode
    if "--headedMode" in cli_args:
        config["headless"] = False

    # Environment override
    for arg in cli_args:
        if arg.startswith("--env="):
            env = arg.split("=")[1].lower()
            if env == "pie1":
                config["baseUrl"] = config.get("baseUrl_pie", config.get("baseUrl"))
            elif env == "stage1":
                config["baseUrl"] = config.get("baseUrl_stg", config.get("baseUrl"))
            else:
                print(f"⚠️ Unknown environment '{env}', using default baseUrl")

    # Optional: fallback defaults
    config.setdefault("browserName", "chrome")
    config.setdefault("headless", True)
    config.setdefault("incognito", True)

    return config

# Add this to the bottom of your existing config_parser.py
# This creates a single instance that can be imported everywhere
config_data = load_config()