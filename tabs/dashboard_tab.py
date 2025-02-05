import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
import requests


class DashboardTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

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

    def load_casinos(self, casinos):
        """Load casinos into the casino selector."""
        self.casino_selector.clear()
        for casino_name in casinos.keys():
            self.casino_selector.addItem(casino_name)

    def load_config(self):
        """Load dashboard-specific settings from files."""
        try:
            # Load offer text
            if os.path.exists(self.parent.offer_file):
                with open(self.parent.offer_file, 'r') as file:
                    offer_text = file.read().strip()
                    self.offer_title.setPlainText(offer_text)

            # Load deposit amount
            if os.path.exists(self.parent.deposit_file):
                with open(self.parent.deposit_file, 'r') as file:
                    deposit_amount = file.read().strip()
                    self.deposit_entry.setText(deposit_amount)

            # Load selected casino title
            if os.path.exists(self.parent.casino_title_file):
                with open(self.parent.casino_title_file, 'r') as file:
                    selected_casino = file.read().strip()
                    index = self.casino_selector.findText(selected_casino)
                    if index >= 0:
                        self.casino_selector.setCurrentIndex(index)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dashboard configuration: {e}")

    def save_config(self):
        # Validate inputs
        if not self.parent.offer_file or not self.parent.deposit_file or not self.parent.casino_title_file:
            self.parent.log_status("Failed to save dashboard configuration: Please complete all fields in the Settings tab.")
            return

        # Save offer text
        try:
            with open(self.parent.offer_file, "w") as f:
                f.write(self.offer_title.toPlainText().strip())
        except Exception as e:
            self.parent.log_status(f"Failed to save offer file: {e}")
            return

        # Save deposit amount
        try:
            deposit_amount = self.deposit_entry.text().strip()
            if not deposit_amount:
                raise ValueError("Deposit amount cannot be empty.")
            with open(self.parent.deposit_file, "w") as f:
                f.write(deposit_amount)
        except Exception as e:
            self.parent.log_status(f"Failed to save deposit file: {e}")
            return

        # Save selected casino title
        try:
            selected_casino = self.casino_selector.currentText()
            if not selected_casino:
                raise ValueError("No casino selected.")
            with open(self.parent.casino_title_file, "w") as f:
                f.write(selected_casino)
        except Exception as e:
            self.parent.log_status(f"Failed to save casino title file: {e}")
            return

        # Log success message
        self.parent.log_status("Dashboard configuration saved successfully.")

    def trigger_spin(self):
        try:
            response = requests.get(self.parent.spin_url)
            self.parent.log_status(f"Spin request sent to {self.parent.spin_url}. Response: {response.status_code}")
        except Exception as e:
            self.parent.log_status(f"Failed to send spin request: {e}")