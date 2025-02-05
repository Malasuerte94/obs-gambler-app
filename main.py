import sys
import os
import json
import time
from PyQt5 import QtWidgets
from tabs.dashboard_tab import DashboardTab
from tabs.casino_manager_tab import CasinoManagerTab
from tabs.youtube_bot_tab import YouTubeBotTab
from tabs.settings_tab import SettingsTab


class GamblerSettingsApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gambler Settings")
        self.setGeometry(100, 100, 600, 500)  # Increase height for the status log

        # Central widget and layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Tab control
        self.tab_control = QtWidgets.QTabWidget()
        layout.addWidget(self.tab_control)

        # Shared attributes
        self.offer_file = ''
        self.deposit_file = ''
        self.casino_title_file = ''
        self.casino_play_image_file = ''
        self.casino_data = {}
        self.bot_commands = ["!referral"]

        # Create tabs
        self.dashboard_tab = DashboardTab(self)
        self.casino_manager_tab = CasinoManagerTab(self)
        self.youtube_bot_tab = YouTubeBotTab(self)
        self.settings_tab = SettingsTab(self)

        # Add tabs to the tab control
        self.tab_control.addTab(self.dashboard_tab, 'Dashboard')
        self.tab_control.addTab(self.casino_manager_tab, 'Casino Manager')
        self.tab_control.addTab(self.youtube_bot_tab, 'YouTube Bot')
        self.tab_control.addTab(self.settings_tab, 'Settings')

        # Status log textbox
        self.status_log = QtWidgets.QTextEdit()
        self.status_log.setReadOnly(True)
        layout.addWidget(self.status_log)

        # Load settings from file
        self.load_settings()

    def log_status(self, message):
        """Log a status message to the status log textbox."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.status_log.append(f"[{timestamp}] {message}")

    def save_settings(self):
        # Save all global settings to settings.json
        settings = {
            'offer_file': self.offer_file,
            'deposit_file': self.deposit_file,
            'casinos': self.casino_data,
            'casino_title_file': self.casino_title_file,
            'casino_play_image_file': self.casino_play_image_file,
            'oauth_port': self.settings_tab.oauth_port.text(),
            'channel_id': self.settings_tab.channel_id.text(),
            'bot_commands': self.bot_commands
        }
        with open('settings.json', 'w') as json_file:
            json.dump(settings, json_file, indent=4)

        # Reload settings in all tabs
        self.load_settings()

        # Log success message
        self.log_status("All settings saved successfully!")

    def load_settings(self):
        try:
            with open('settings.json', 'r') as json_file:
                settings = json.load(json_file)

            # Load global settings
            self.offer_file = settings.get('offer_file', '')
            self.deposit_file = settings.get('deposit_file', '')
            self.casino_data = settings.get('casinos', {})
            self.casino_title_file = settings.get('casino_title_file', '')
            self.casino_play_image_file = settings.get('casino_play_image_file', '')
            self.bot_commands = settings.get('bot_commands', ["!referral"])

            # Pass settings to tabs
            self.settings_tab.load_settings(settings)
            self.youtube_bot_tab.load_settings(settings)
            self.casino_manager_tab.load_casinos(self.casino_data)
            self.dashboard_tab.load_casinos(self.casino_data)
            self.dashboard_tab.load_config()

            # Log success message
            self.log_status("Settings loaded successfully.")

        except FileNotFoundError:
            self.log_status("No settings file found. Starting with default settings.")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GamblerSettingsApp()
    window.show()
    sys.exit(app.exec_())