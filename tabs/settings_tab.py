from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog

class SettingsTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        tab_widget = QtWidgets.QTabWidget()
        layout.addWidget(tab_widget)

        api_settings = self.create_api_settings()
        casino_settings = self.create_casino_settings()
        youtube_settings = self.create_youtube_settings()
        kick_settings = self.create_kick_settings()
        chat_settings = self.create_chat_settings()

        tab_widget.addTab(api_settings, "API Settings")
        tab_widget.addTab(casino_settings, "Casino Settings")
        tab_widget.addTab(youtube_settings, "YouTube Settings")
        tab_widget.addTab(kick_settings, "Kick Settings")
        tab_widget.addTab(chat_settings, "Chat Settings")

        save_button = QtWidgets.QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.load_settings()

    def create_api_settings(self):
        api_settings = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(api_settings)

        self.api_url_entry = QtWidgets.QLineEdit()
        layout.addRow("API URL:", self.api_url_entry)

        self.api_streamer_id_entry = QtWidgets.QLineEdit()
        layout.addRow("Streamer ID:", self.api_streamer_id_entry)

        return api_settings

    def create_casino_settings(self):
        casino_settings = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(casino_settings)

        self.offer_entry = QtWidgets.QLineEdit()
        offer_button = QtWidgets.QPushButton("Browse")
        offer_button.clicked.connect(self.browse_offer_file)
        layout.addRow("Offer File:", self.offer_entry)
        layout.addRow("", offer_button)

        self.deposit_entry = QtWidgets.QLineEdit()
        deposit_button = QtWidgets.QPushButton("Browse")
        deposit_button.clicked.connect(self.browse_deposit_file)
        layout.addRow("Deposit File:", self.deposit_entry)
        layout.addRow("", deposit_button)

        self.casino_play_image_entry = QtWidgets.QLineEdit()
        play_image_button = QtWidgets.QPushButton("Browse")
        play_image_button.clicked.connect(self.browse_play_image_file)
        layout.addRow("Casino Play Image:", self.casino_play_image_entry)
        layout.addRow("", play_image_button)

        self.casino_title_entry = QtWidgets.QLineEdit()
        casino_title_button = QtWidgets.QPushButton("Browse")
        casino_title_button.clicked.connect(self.browse_casino_title_file)
        layout.addRow("Casino Title File:", self.casino_title_entry)
        layout.addRow("", casino_title_button)

        return casino_settings

    def create_youtube_settings(self):
        youtube_settings = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(youtube_settings)

        self.youtube_api_entry = QtWidgets.QLineEdit()
        layout.addRow("YouTube API Key:", self.youtube_api_entry)

        self.yt_channel_entry = QtWidgets.QLineEdit()
        layout.addRow("YouTube Channel ID:", self.yt_channel_entry)

        return youtube_settings

    def create_kick_settings(self):
        kick_settings = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(kick_settings)

        self.kick_channel_entry = QtWidgets.QLineEdit()
        layout.addRow("Kick Channel:", self.kick_channel_entry)

        return kick_settings

    def create_chat_settings(self):
        chat_settings = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(chat_settings)

        self.points_entry = QtWidgets.QLineEdit()
        self.interval_entry = QtWidgets.QLineEdit()
        layout.addRow("Points:", self.points_entry)
        layout.addRow("Interval (minutes):", self.interval_entry)

        self.ignored_users_entry = QtWidgets.QLineEdit()
        layout.addRow("Ignored Users:", self.ignored_users_entry)

        return chat_settings

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
        self.parent.settings.set("api_url", self.api_url_entry.text().strip())
        self.parent.settings.set("streamer_id", self.api_streamer_id_entry.text().strip())
        self.parent.settings.set("offer_file", self.offer_entry.text().strip())
        self.parent.settings.set("deposit_file", self.deposit_entry.text().strip())
        self.parent.settings.set("casino_play_image_file", self.casino_play_image_entry.text().strip())
        self.parent.settings.set("casino_title_file", self.casino_title_entry.text().strip())
        self.parent.settings.set("youtube_api", self.youtube_api_entry.text().strip())
        self.parent.settings.set("yt_channel", self.yt_channel_entry.text().strip())
        self.parent.settings.set("kick_channel", self.kick_channel_entry.text().strip())
        self.parent.settings.set("chat_points", self.points_entry.text().strip())
        self.parent.settings.set("chat_interval", self.interval_entry.text().strip())
        self.parent.settings.set("ignored_users", self.ignored_users_entry.text().strip())

        self.parent.log_status("Settings saved successfully.")

    def load_settings(self):
        self.api_url_entry.setText(self.parent.settings.get('api_url', ''))
        self.api_streamer_id_entry.setText(self.parent.settings.get('streamer_id', ''))
        self.offer_entry.setText(self.parent.settings.get('offer_file', ''))
        self.deposit_entry.setText(self.parent.settings.get('deposit_file', ''))
        self.casino_play_image_entry.setText(self.parent.settings.get('casino_play_image_file', ''))
        self.casino_title_entry.setText(self.parent.settings.get('casino_title_file', ''))
        self.youtube_api_entry.setText(self.parent.settings.get('youtube_api', ''))
        self.yt_channel_entry.setText(self.parent.settings.get('yt_channel', ''))
        self.kick_channel_entry.setText(self.parent.settings.get('kick_channel', ''))
        self.points_entry.setText(self.parent.settings.get('chat_points', ''))
        self.interval_entry.setText(self.parent.settings.get('chat_interval', ''))
        self.ignored_users_entry.setText(self.parent.settings.get('ignored_users', ''))