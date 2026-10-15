import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    """Loads settings from the JSON file, or creates defaults if missing."""
    default_settings = {
        "sound_volume": 80,
        "mobile_controls": False
    }
    
    if not os.path.exists(SETTINGS_FILE):
        save_settings(default_settings)
        return default_settings
        
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return default_settings

def save_settings(settings):
    """Saves settings to the JSON file."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")