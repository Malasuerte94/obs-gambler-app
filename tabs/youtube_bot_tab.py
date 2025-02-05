from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
import threading
from youtube_bot import YouTubeBot


class YouTubeBotTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bot_thread = None
        self.bot_running = False
        self.bot = None
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QGridLayout(self)

        # Start/Stop Bot Button
        self.bot_status_label = QtWidgets.QLabel("Bot Status: Stopped")
        layout.addWidget(self.bot_status_label, 0, 0)
        self.start_stop_button = QtWidgets.QPushButton("Start Bot")
        self.start_stop_button.clicked.connect(self.toggle_bot)
        layout.addWidget(self.start_stop_button, 0, 1)

        # Edit Commands
        layout.addWidget(QtWidgets.QLabel("Accepted Commands:"), 1, 0)
        self.commands_text = QtWidgets.QTextEdit()
        self.commands_text.setText("\n".join(self.parent.bot_commands))
        layout.addWidget(self.commands_text, 2, 0, 1, 2)

        # Save Commands Button
        save_commands_button = QtWidgets.QPushButton("Save Commands")
        save_commands_button.clicked.connect(self.save_bot_commands)
        layout.addWidget(save_commands_button, 3, 1)

    def toggle_bot(self):
        if not self.bot_running:
            # Start the bot
            self.bot_running = True
            self.start_stop_button.setText("Stop Bot")
            self.bot_status_label.setText("Bot Status: Running")

            port = int(self.parent.settings_tab.oauth_port.text())
            channel_id = self.parent.settings_tab.channel_id.text()
            self.bot = YouTubeBot(port=port, channel_id=channel_id, commands=self.parent.bot_commands)

            self.bot_thread = threading.Thread(target=self.bot.run)
            self.bot_thread.daemon = True
            self.bot_thread.start()
        else:
            # Stop the bot
            if self.bot:
                self.bot.stop()
            self.bot_running = False
            self.start_stop_button.setText("Start Bot")
            self.bot_status_label.setText("Bot Status: Stopped")

    def save_bot_commands(self):
        # Parse the commands from the text area
        commands = self.commands_text.toPlainText().split("\n")
        self.parent.bot_commands = [cmd.strip() for cmd in commands if cmd.strip()]

        # Save the updated bot commands to settings.json
        self.parent.save_settings()

        self.parent.log_status("Bot commands saved successfully.")

    def load_settings(self, settings):
        self.commands_text.setText("\n".join(settings.get('bot_commands', ["!referral"])))