import json
import os


class SettingsManager:
    def __init__(self, filename="settings.json"):
        """Initialize SettingsManager with the specified file."""
        self.filename = filename
        self.settings = {}

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as file:
                    self.settings = json.load(file)
            except json.JSONDecodeError:
                print("Error: Failed to decode JSON. Loading default settings.")
                self.settings = {}
        else:
            print("Settings file not found. Using default settings.")
            self.settings = {}

        return self.settings

    def save(self, new_settings):
        """Save the provided settings dictionary to a JSON file."""
        try:
            with open(self.filename, "w") as file:
                json.dump(new_settings, file, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        """Retrieve a specific setting value with a default fallback."""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set a specific setting value and save the changes."""
        self.settings[key] = value
        self.save(self.settings)
