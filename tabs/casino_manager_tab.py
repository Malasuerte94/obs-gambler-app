from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QLabel
from utils.api_client import APIClient
import os

class CasinoManagerTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.api_client = APIClient(parent.settings)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        # Form for adding a new casino
        form_layout = QtWidgets.QGridLayout()
        form_layout.addWidget(QtWidgets.QLabel("Casino Name:"), 0, 0)
        self.new_casino_name = QtWidgets.QLineEdit()
        form_layout.addWidget(self.new_casino_name, 0, 1)

        form_layout.addWidget(QtWidgets.QLabel("Casino URL:"), 1, 0)
        self.new_casino_url = QtWidgets.QLineEdit()
        form_layout.addWidget(self.new_casino_url, 1, 1)

        form_layout.addWidget(QtWidgets.QLabel("Casino Logo:"), 2, 0)
        self.logo_entry = QtWidgets.QLineEdit()
        form_layout.addWidget(self.logo_entry, 2, 1)
        browse_button = QtWidgets.QPushButton("Browse")
        browse_button.clicked.connect(self.browse_logo_file)
        form_layout.addWidget(browse_button, 2, 2)

        add_casino_button = QtWidgets.QPushButton("Add Casino")
        add_casino_button.clicked.connect(self.add_casino)
        form_layout.addWidget(add_casino_button, 3, 1)

        layout.addLayout(form_layout)

        # Table to display casinos
        self.casino_table = QTableWidget()
        self.casino_table.setColumnCount(3)
        self.casino_table.setHorizontalHeaderLabels(["Casino Name", "URL", "Logo"])
        self.casino_table.setColumnWidth(0, 200)
        self.casino_table.setColumnWidth(1, 250)
        self.casino_table.setColumnWidth(2, 100)
        # Apply dark mode styling to the table header and background
        self.casino_table.setStyleSheet("""
            QTableWidget {
                background-color: #222;
                color: white;
                gridline-color: #444;
                selection-background-color: #444;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #333;
                color: white;
                padding: 4px;
                border: 1px solid #444;
            }
            QTableCornerButton::section {
                background-color: #333;
                border: 1px solid #444;
            }
        """)
        layout.addWidget(self.casino_table)

        # Load existing casinos from API
        self.load_casinos()

    def browse_logo_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Logo File", "", "Image Files (*.png *.jpg *.jpeg)")
        if filename:
            self.logo_entry.setText(filename)

    def add_casino(self):
        """Send a request to the API to add a new casino."""
        name = self.new_casino_name.text().strip()
        url = self.new_casino_url.text().strip()
        logo_path = self.logo_entry.text().strip()

        if not name or not url or not logo_path:
            self.parent.log_status("Error: Please fill all fields before adding a casino.")
            return

        try:
            with open(logo_path, "rb") as logo_file:
                files = {"image": (os.path.basename(logo_path), logo_file, "image/png")}
                data = {"name": name, "url": url}

                response = self.api_client.post("add-casino", data=data, files=files)

            # Handle cases where response is None
            if response is None:
                self.parent.log_status("Error: No response from API.")
                return

            # Handle error messages from API
            if "error" in response:
                self.parent.log_status(f"Error: {response['error']}")
                return

            # Success response
            if response.get("success"):
                self.parent.log_status(f"Casino '{name}' added successfully.")
                self.load_casinos()  # Refresh table
            else:
                self.parent.log_status("Error: Unexpected API response.")

        except Exception as e:
            self.parent.log_status(f"Error: Failed to upload image - {e}")

    def load_casinos(self):
        """Fetch the list of casinos from the API and populate the table with images."""
        self.casino_table.setRowCount(0)  # Clear previous table content

        response = self.api_client.get("get-casinos")
        if not response:
            self.parent.log_status("Error: Unable to fetch casinos from API.")
            return

        casinos = response.get("casinos", [])  # Extract the list of casinos

        for row_idx, casino in enumerate(casinos):
            self.casino_table.insertRow(row_idx)

            # Casino Logo - Load and Display Image
            logo_label = QLabel()
            logo_url = casino.get("logo", "")
            if logo_url:
                pixmap = QPixmap()
                pixmap.loadFromData(APIClient.get_url(logo_url, return_raw=True))  # Load image data
                pixmap = pixmap.scaled(80, 50)  # Resize for table cell

                logo_label.setPixmap(pixmap)
                logo_label.setAlignment(QtCore.Qt.AlignCenter)

            self.casino_table.setCellWidget(row_idx, 0, logo_label)

            # Casino Name
            name_item = QTableWidgetItem(casino.get("name", ""))
            name_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)  # Read-only
            self.casino_table.setItem(row_idx, 1, name_item)

            # Casino URL
            url_item = QTableWidgetItem(casino.get("url", ""))
            url_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)  # Read-only
            self.casino_table.setItem(row_idx, 2, url_item)

        self.parent.log_status("Casinos loaded successfully.")
