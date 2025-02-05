from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PIL import Image


class CasinoManagerTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QGridLayout(self)

        # Add New Casino Section
        layout.addWidget(QtWidgets.QLabel("Add New Casino"), 0, 0, 1, 2)
        layout.addWidget(QtWidgets.QLabel("Casino Title:"), 1, 0)
        self.new_casino_title = QtWidgets.QLineEdit()
        layout.addWidget(self.new_casino_title, 1, 1)

        layout.addWidget(QtWidgets.QLabel("Casino Logo:"), 2, 0)
        self.logo_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.logo_entry, 2, 1)
        logo_button = QtWidgets.QPushButton("Browse")
        logo_button.clicked.connect(self.browse_logo_file)
        layout.addWidget(logo_button, 2, 2)

        add_casino_button = QtWidgets.QPushButton("Add Casino")
        add_casino_button.clicked.connect(self.add_casino)
        layout.addWidget(add_casino_button, 3, 1)

        remove_casino_button = QtWidgets.QPushButton("Remove Selected Casino")
        remove_casino_button.clicked.connect(self.remove_selected_casino)
        layout.addWidget(remove_casino_button, 4, 1)

        self.casino_listbox = QtWidgets.QListWidget()
        layout.addWidget(self.casino_listbox, 5, 0, 1, 3)

    def browse_logo_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Logo File", "", "Image Files (*.png *.jpg *.jpeg)")
        if filename:
            self.logo_entry.setText(filename)

    def add_casino(self):
        title = self.new_casino_title.text()
        logo_path = self.logo_entry.text()
        if title and logo_path:
            # Add the casino to the parent's casino_data dictionary
            self.parent.casino_data[title] = logo_path

            # Update the casino listbox
            self.casino_listbox.addItem(title)

            # Clear input fields
            self.new_casino_title.clear()
            self.logo_entry.clear()

            # Save the updated casino data to settings.json
            self.parent.save_settings()

            QMessageBox.information(self, "Success", "Casino added successfully!")
        else:
            QMessageBox.warning(self, "Warning", "Please complete all fields.")

    def remove_selected_casino(self):
        selected_items = self.casino_listbox.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a casino to remove.")
            return

        for item in selected_items:
            casino_title = item.text()

            # Remove the casino from the parent's casino_data dictionary
            if casino_title in self.parent.casino_data:
                del self.parent.casino_data[casino_title]

            # Remove the casino from the casino listbox
            self.casino_listbox.takeItem(self.casino_listbox.row(item))

        # Save the updated casino data to settings.json
        self.parent.save_settings()

    def load_casinos(self, casinos):
        self.casino_listbox.clear()
        for casino_name in casinos.keys():
            self.casino_listbox.addItem(casino_name)