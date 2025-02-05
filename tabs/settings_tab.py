from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox


class SettingsTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QGridLayout(self)

        # Offer File Input
        layout.addWidget(QtWidgets.QLabel("Select Target Text File for Offer:"), 0, 0)
        self.offer_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.offer_entry, 0, 1)
        offer_button = QtWidgets.QPushButton("Browse")
        offer_button.clicked.connect(self.browse_title_file)
        layout.addWidget(offer_button, 0, 2)

        # Deposit File Input
        layout.addWidget(QtWidgets.QLabel("Select Target Text File for Deposit:"), 1, 0)
        self.deposit_entry_file = QtWidgets.QLineEdit()
        layout.addWidget(self.deposit_entry_file, 1, 1)
        deposit_button = QtWidgets.QPushButton("Browse")
        deposit_button.clicked.connect(self.browse_deposit_file)
        layout.addWidget(deposit_button, 1, 2)

        # Casino Play Image Location Input
        layout.addWidget(QtWidgets.QLabel("Select Target Location for Casino Play Image:"), 2, 0)
        self.casino_play_image_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.casino_play_image_entry, 2, 1)
        play_image_button = QtWidgets.QPushButton("Browse")
        play_image_button.clicked.connect(self.browse_play_image_file)
        layout.addWidget(play_image_button, 2, 2)

        # Casino Title File Input
        layout.addWidget(QtWidgets.QLabel("Select Target Text File for Selected Casino Title:"), 3, 0)
        self.casino_title_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.casino_title_entry, 3, 1)
        casino_title_button = QtWidgets.QPushButton("Browse")
        casino_title_button.clicked.connect(self.browse_casino_title_file)
        layout.addWidget(casino_title_button, 3, 2)

        # OAuth Port Input
        layout.addWidget(QtWidgets.QLabel("OAuth Port:"), 4, 0)
        self.oauth_port = QtWidgets.QLineEdit()
        self.oauth_port.setText("8080")
        layout.addWidget(self.oauth_port, 4, 1)

        # YouTube Channel ID Input
        layout.addWidget(QtWidgets.QLabel("YouTube Channel ID:"), 5, 0)
        self.channel_id = QtWidgets.QLineEdit()
        layout.addWidget(self.channel_id, 5, 1)

        # Spin URL Input
        layout.addWidget(QtWidgets.QLabel("Spin URL:"), 6, 0)
        self.spin_url_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.spin_url_entry, 6, 1)

        # YouTube Channel Input
        layout.addWidget(QtWidgets.QLabel("YouTube Channel:"), 7, 0)
        self.yt_channel_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.yt_channel_entry, 7, 1)

        # Kick Channel Input
        layout.addWidget(QtWidgets.QLabel("Kick Channel:"), 8, 0)
        self.kick_channel_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.kick_channel_entry, 8, 1)

        # Save Button
        save_button = QtWidgets.QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button, 9, 1)

    def browse_title_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Offer File", "", "Text Files (*.txt)")
        if filename:
            self.parent.offer_file = filename
            self.offer_entry.setText(filename)

    def browse_deposit_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Deposit File", "", "Text Files (*.txt)")
        if filename:
            self.parent.deposit_file = filename
            self.deposit_entry_file.setText(filename)

    def browse_play_image_file(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Play Image Directory")
        if directory:
            self.parent.casino_play_image_file = directory
            self.casino_play_image_entry.setText(directory)

    def browse_casino_title_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Casino Title File", "", "Text Files (*.txt)")
        if filename:
            self.parent.casino_title_file = filename
            self.casino_title_entry.setText(filename)
    
    def save_settings(self):
        self.parent.spin_url = self.spin_url_entry.text().strip()
        self.parent.yt_channel = self.yt_channel_entry.text().strip()
        self.parent.kick_channel = self.kick_channel_entry.text().strip()

        # Call the parent's save_settings method
        self.parent.save_settings()

    def load_settings(self, settings):
        self.offer_entry.setText(settings.get('offer_file', ''))
        self.deposit_entry_file.setText(settings.get('deposit_file', ''))
        self.casino_title_entry.setText(settings.get('casino_title_file', ''))
        self.casino_play_image_entry.setText(settings.get('casino_play_image_file', ''))
        self.oauth_port.setText(settings.get('oauth_port', '8080'))
        self.channel_id.setText(settings.get('channel_id', ''))
        self.spin_url_entry.setText(settings.get('spin_url', "https://pacanele.catalin-ene.ro/api/spin/12"))
        self.yt_channel_entry.setText(settings.get('yt_channel', ""))
        self.kick_channel_entry.setText(settings.get('kick_channel', ""))