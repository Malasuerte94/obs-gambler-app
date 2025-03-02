import os

import requests
from PyQt5 import QtWidgets
from utils.api_client import APIClient  # Import API Client to fetch casinos

class DashboardTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        print(parent.settings)
        self.parent = parent
        self.api_client = APIClient(parent.settings)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QtWidgets.QGridLayout(self)

        # Offer Input
        layout.addWidget(QtWidgets.QLabel("Offer:"), 1, 0)
        self.offer_title = QtWidgets.QTextEdit()
        layout.addWidget(self.offer_title, 1, 1)

        # Casino Selector
        layout.addWidget(QtWidgets.QLabel("Select Casino:"), 0, 0)
        self.casino_selector = QtWidgets.QComboBox()
        layout.addWidget(self.casino_selector, 0, 1)

        # Refresh button for casino list
        refresh_button = QtWidgets.QPushButton("🔄 Refresh Casinos")
        refresh_button.clicked.connect(self.load_casinos_from_api)
        layout.addWidget(refresh_button, 0, 2)

        # Deposit Amount Input
        layout.addWidget(QtWidgets.QLabel("Deposit Amount:"), 2, 0)
        self.deposit_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.deposit_entry, 2, 1)

        # Save Button
        save_button = QtWidgets.QPushButton("SAVE")
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button, 3, 1)

        # SPIN Button
        spin_button = QtWidgets.QPushButton("SPIN")
        spin_button.clicked.connect(self.trigger_spin)
        layout.addWidget(spin_button, 4, 1)

        self.load_settings()
        # Load casino list from API
        self.load_casinos_from_api()

    def load_casinos_from_api(self):
        """Fetch the casino list from API and populate the dropdown."""
        self.casino_selector.clear()
        response = self.api_client.get("get-casinos")  # API call

        if not response or "casinos" not in response:
            self.parent.log_status("Error: Unable to fetch casinos from API.")
            return

        casinos = response["casinos"]
        for casino in casinos:
            self.casino_selector.addItem(casino["name"])

        self.parent.log_status("Casino list updated successfully.")

    def load_settings(self):
        """Load settings and update UI elements with actual file contents."""

        # Load offer file path from settings
        offer_file = self.parent.settings.get('offer_file', '')
        if offer_file and os.path.exists(offer_file):
            try:
                with open(offer_file, "r") as f:
                    self.offer_title.setPlainText(f.read().strip())
            except Exception as e:
                self.parent.log_status(f"Error reading offer file: {e}")
        else:
            self.parent.log_status("Offer file not found. Set it in the Settings tab.")

        # Load deposit file path from settings
        deposit_file = self.parent.settings.get('deposit_file', '')
        if deposit_file and os.path.exists(deposit_file):
            try:
                with open(deposit_file, "r") as f:
                    self.deposit_entry.setText(f.read().strip())
            except Exception as e:
                self.parent.log_status(f"Error reading deposit file: {e}")
        else:
            self.parent.log_status("Deposit file not found. Set it in the Settings tab.")

        # Load casinos from API
        self.load_casinos_from_api()

    import requests

    def save_config(self):
        """Save the offer and deposit values and download the selected casino's logo."""

        # Load the offer and deposit file paths from settings
        offer_file = self.parent.settings.get("offer_file", "")
        deposit_file = self.parent.settings.get("deposit_file", "")
        selected_casino = self.casino_selector.currentText()

        # Validate that the paths exist before writing
        if not offer_file or not deposit_file or not selected_casino:
            self.parent.log_status("Error: Offer file, deposit file, or casino selection missing.")
            return

        try:
            # Save the offer text inside the offer file
            with open(offer_file, "w") as f:
                f.write(self.offer_title.toPlainText().strip())
        except Exception as e:
            self.parent.log_status(f"Failed to save offer: {e}")
            return

        try:
            # Save the deposit amount inside the deposit file
            with open(deposit_file, "w") as f:
                f.write(self.deposit_entry.text().strip())
        except Exception as e:
            self.parent.log_status(f"Failed to save deposit: {e}")
            return

        # Fetch selected casino details from the API
        response = self.api_client.get("get-casinos")
        if not response or "casinos" not in response:
            self.parent.log_status("Error: Unable to fetch casinos from API.")
            return

        casinos = response["casinos"]
        selected_casino_data = next((c for c in casinos if c["name"] == selected_casino), None)

        if not selected_casino_data or "logo" not in selected_casino_data:
            self.parent.log_status("Error: Casino logo not found.")
            return

        logo_url = selected_casino_data["logo"]  # Casino logo URL from API

        # Download and save the casino logo as play_on_casino.png
        try:
            logo_response = requests.get(logo_url, stream=True)
            logo_response.raise_for_status()

            with open("play_on_casino.png", "wb") as file:
                for chunk in logo_response.iter_content(1024):
                    file.write(chunk)

            self.parent.log_status(f"Casino image saved as play_on_casino.png")

        except Exception as e:
            self.parent.log_status(f"Error: Failed to download casino logo - {e}")

        # Save selected casino in settings
        self.parent.settings["selected_casino"] = selected_casino
        self.parent.settings_manager.save(self.parent.settings)

        self.parent.log_status(f"Dashboard settings saved successfully. Selected Casino: {selected_casino}")

    def trigger_spin(self):
        """Send a request to trigger a spin."""
        spin_url = self.parent.settings.get("spin_url", "")
        if not spin_url:
            self.parent.log_status("Spin URL not configured.")
            return

        try:
            import requests
            response = requests.get(spin_url)
            self.parent.log_status(f"Spin request sent. Response: {response.status_code}")
        except Exception as e:
            self.parent.log_status(f"Failed to send spin request: {e}")
