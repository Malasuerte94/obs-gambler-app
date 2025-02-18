from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog

class SettingsTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QGridLayout(self)

        # Offer File Input
        layout.addWidget(QtWidgets.QLabel("Select Offer File:"), 0, 0)
        self.offer_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.offer_entry, 0, 1)
        offer_button = QtWidgets.QPushButton("Browse")
        offer_button.clicked.connect(self.browse_offer_file)
        layout.addWidget(offer_button, 0, 2)

        # Deposit File Input
        layout.addWidget(QtWidgets.QLabel("Select Deposit File:"), 1, 0)
        self.deposit_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.deposit_entry, 1, 1)
        deposit_button = QtWidgets.QPushButton("Browse")
        deposit_button.clicked.connect(self.browse_deposit_file)
        layout.addWidget(deposit_button, 1, 2)

        # Casino Play Image Location
        layout.addWidget(QtWidgets.QLabel("Casino Play Image:"), 2, 0)
        self.casino_play_image_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.casino_play_image_entry, 2, 1)
        play_image_button = QtWidgets.QPushButton("Browse")
        play_image_button.clicked.connect(self.browse_play_image_file)
        layout.addWidget(play_image_button, 2, 2)

        # Casino Title File Input
        layout.addWidget(QtWidgets.QLabel("Casino Title File:"), 3, 0)
        self.casino_title_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.casino_title_entry, 3, 1)
        casino_title_button = QtWidgets.QPushButton("Browse")
        casino_title_button.clicked.connect(self.browse_casino_title_file)
        layout.addWidget(casino_title_button, 3, 2)

        # YouTube API Key
        layout.addWidget(QtWidgets.QLabel("YouTube API Key:"), 4, 0)
        self.youtube_api_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.youtube_api_entry, 4, 1)

        # YouTube Channel ID
        layout.addWidget(QtWidgets.QLabel("YouTube Channel ID:"), 5, 0)
        self.yt_channel_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.yt_channel_entry, 5, 1)

        # Spin URL
        layout.addWidget(QtWidgets.QLabel("Spin URL:"), 6, 0)
        self.spin_url_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.spin_url_entry, 6, 1)

        # Kick Channel
        layout.addWidget(QtWidgets.QLabel("Kick Channel:"), 7, 0)
        self.kick_channel_entry = QtWidgets.QLineEdit()
        layout.addWidget(self.kick_channel_entry, 7, 1)

        # Save Button
        save_button = QtWidgets.QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button, 8, 1)

    def browse_offer_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Offer File", "", "Text Files (*.txt)")
        if filename:
            self.offer_entry.setText(filename)

    def browse_deposit_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Deposit File", "", "Text Files (*.txt)")
        if filename:
            self.deposit_entry.setText(filename)

    def browse_play_image_file(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Play Image Directory")
        if directory:
            self.casino_play_image_entry.setText(directory)

    def browse_casino_title_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Casino Title File", "", "Text Files (*.txt)")
        if filename:
            self.casino_title_entry.setText(filename)

    def save_settings(self):
        """Save the settings using the parent's settings manager."""
        self.parent.settings.set("offer_file", self.offer_entry.text().strip())
        self.parent.settings.set("deposit_file", self.deposit_entry.text().strip())
        self.parent.settings.set("casino_play_image_file", self.casino_play_image_entry.text().strip())
        self.parent.settings.set("casino_title_file", self.casino_title_entry.text().strip())
        self.parent.settings.set("youtube_api", self.youtube_api_entry.text().strip())
        self.parent.settings.set("yt_channel", self.yt_channel_entry.text().strip())
        self.parent.settings.set("spin_url", self.spin_url_entry.text().strip())
        self.parent.settings.set("kick_channel", self.kick_channel_entry.text().strip())

        self.parent.log_status("Settings saved successfully.")

    def load_settings(self, settings):
        """Load settings from the settings manager."""
        self.offer_entry.setText(settings.get('offer_file', ''))
        self.deposit_entry.setText(settings.get('deposit_file', ''))
        self.casino_play_image_entry.setText(settings.get('casino_play_image_file', ''))
        self.casino_title_entry.setText(settings.get('casino_title_file', ''))
        self.youtube_api_entry.setText(settings.get('youtube_api', ''))
        self.yt_channel_entry.setText(settings.get('yt_channel', ''))
        self.spin_url_entry.setText(settings.get('spin_url', ''))
        self.kick_channel_entry.setText(settings.get('kick_channel', ''))
