import datetime
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView

from tabs.youtube_watcher.youtube_chat import get_live_video_id, analyze_hot_message, analyze_top_messages
from tabs.youtube_watcher.youtube_hot_word import update_hotword_html


class YouTubeWatcherTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # Maintain chat history (up to 500 messages) and track seen messages by ID
        self.chat_history = []
        self.seen_message_ids = set()  # Store message IDs to avoid duplicates
        self.last_hotword = None
        self.last_percent = None
        self.last_top3 = None

        # Create a horizontal splitter for three panes.
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)

        # Left pane: a widget to hold hotword label and TOP 3 checkbox.
        self.hotword_label = QtWidgets.QLabel("HOT-WORD: N/A")
        self.hotword_label.setAlignment(QtCore.Qt.AlignCenter)
        self.hotword_label.setFixedWidth(150)
        self.top3_checkbox = QtWidgets.QCheckBox("TOP 3")
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.hotword_label)
        left_layout.addWidget(self.top3_checkbox)
        left_layout.addStretch()
        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(left_layout)
        self.splitter.addWidget(left_widget)

        # Middle pane: Chat log stored in a dark-themed table
        self.chat_table = QtWidgets.QTableWidget()
        self.chat_table.setColumnCount(4)
        self.chat_table.setHorizontalHeaderLabels(["User", "Message", "Member", "Date-Time"])
        self.chat_table.setColumnWidth(0, 150)  # User
        self.chat_table.setColumnWidth(1, 400)  # Message
        self.chat_table.setColumnWidth(2, 80)   # Member
        self.chat_table.setColumnWidth(3, 120)  # Date-Time

        # Apply dark mode styling to the table
        self.chat_table.setStyleSheet("""
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

        self.splitter.addWidget(self.chat_table)

        # Right pane: Chat webpage.
        self.chat_view = QWebEngineView()
        self.splitter.addWidget(self.chat_view)

        self.splitter.setSizes([150, 400, 800])
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.splitter)

    def load_settings(self, settings):
        """Load YouTube API key and channel from settings."""
        youtube_api = settings.get("youtube_api", "")
        yt_channel = settings.get("yt_channel", "")

        self.youtube_api = youtube_api
        self.yt_channel = yt_channel
        self.chat_table.setRowCount(0)  # Clear previous chat
        self.parent.log_status("Checking for live stream on channel: " + yt_channel)

        try:
            live_video_id = get_live_video_id(yt_channel, youtube_api)
            if live_video_id:
                self.parent.log_status("Live video found: " + live_video_id)
                chat_url = "https://www.youtube.com/live_chat?v=" + live_video_id
                self.parent.log_status("Loading chat URL: " + chat_url)
                self.chat_view.setUrl(QtCore.QUrl(chat_url))
                self.chat_view.loadFinished.connect(self.onChatLoadFinished)
            else:
                self.parent.log_status("No live video is currently streaming.")
        except Exception as e:
            self.parent.log_status("Error while checking live status: " + str(e))

    def onChatLoadFinished(self, ok):
        if ok:
            self.parent.log_status("Chat page loaded successfully. Starting extraction...")
            self.chat_timer = QtCore.QTimer(self)
            self.chat_timer.timeout.connect(self.extractChatMessages)
            self.chat_timer.start(1000)
        else:
            self.parent.log_status("Failed to load chat page.")

    def extractChatMessages(self):
        js_extract = """
        (function(){
            var messages = [];
            var chatElements = document.querySelectorAll("yt-live-chat-text-message-renderer");
            for (var i = 0; i < chatElements.length; i++) {
                var msgId = chatElements[i].id;
                var userElem = chatElements[i].querySelector("#author-name");
                var messageElem = chatElements[i].querySelector("#message");
                var memberBadge = chatElements[i].querySelector("yt-live-chat-author-badge-renderer");

                var user = userElem ? userElem.innerText.trim() : "Unknown";
                var msg = messageElem ? messageElem.innerText.trim() : "";
                var member = memberBadge ? "Yes" : "No";

                messages.push(msgId + "||" + user + "||" + msg + "||" + member);
            }
            messages.reverse();
            return messages.join("\\n");
        })();
        """
        self.chat_view.page().runJavaScript(js_extract, self.handleChatMessages)

    def handleChatMessages(self, result):
        if result is not None:
            new_msgs = result.split("\n")
            for msg in new_msgs:
                parts = msg.split("||")
                if len(parts) == 4:
                    msg_id, user, message, member_status = parts
                    if msg_id not in self.seen_message_ids:  # Only add new messages
                        self.seen_message_ids.add(msg_id)
                        self.add_message_to_table(user, message, member_status)

            self.save_chat_to_file()
            self.update_hotwords()

        else:
            self.parent.log_status("No chat messages extracted.")

    def add_message_to_table(self, user, message, member_status):
        """Adds a new chat message to the table at the top (newest first) with timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.chat_table.insertRow(0)  # Insert at the top
        self.chat_table.setItem(0, 0, QtWidgets.QTableWidgetItem(user))
        self.chat_table.setItem(0, 1, QtWidgets.QTableWidgetItem(message))
        self.chat_table.setItem(0, 2, QtWidgets.QTableWidgetItem(member_status))
        self.chat_table.setItem(0, 3, QtWidgets.QTableWidgetItem(timestamp))

        # Keep only the last 500 messages
        while self.chat_table.rowCount() > 1000:
            self.chat_table.removeRow(1000)

    def save_chat_to_file(self):
        """Save the last 500 chat messages to a text file."""
        try:
            with open("youtube_chat_log.txt", "w", encoding="utf-8") as f:
                for row in range(self.chat_table.rowCount()):
                    user = self.chat_table.item(row, 0).text()
                    message = self.chat_table.item(row, 1).text()
                    member = self.chat_table.item(row, 2).text()
                    timestamp = self.chat_table.item(row, 3).text()
                    f.write(f"{timestamp} || {user} || {member} || {message}\n")
        except Exception as e:
            self.parent.log_status(f"Error saving chat log: {e}")

    def update_hotwords(self):
        """Analyzes the chat messages and updates the hotword label and HTML display."""
        try:
            # Ensure messages are not empty and contain valid data
            messages = [
                self.chat_table.item(row, 1).text().strip()
                for row in range(self.chat_table.rowCount())
                if self.chat_table.item(row, 1) and self.chat_table.item(row, 1).text().strip()
            ]

            if len(messages) < 30:
                self.hotword_label.setText("HOT-WORD: Not enough data")
                return

            if not messages:
                self.hotword_label.setText("HOT-WORD: N/A")
                return

            if self.top3_checkbox.isChecked():
                top3 = analyze_top_messages(messages, top_n=3)
                if top3:
                    self.hotword_label.setText(f"TOP 3: {', '.join([word for word, _ in top3])}")
                    update_hotword_html(None, None, top3=top3)
                else:
                    self.hotword_label.setText("HOT-WORD: N/A")
            else:
                hotword, percent = analyze_hot_message(messages)

                if hotword:
                    self.hotword_label.setText(f"HOT-WORD: {hotword.upper()} {percent:.1f}%")
                    update_hotword_html(hotword, percent)
                else:
                    self.hotword_label.setText("HOT-WORD: N/A")

        except IndexError as e:
            self.parent.log_status(f"Error updating hotwords: List index out of range - {e}")

        except Exception as e:
            self.parent.log_status(f"Unexpected error in update_hotwords: {e}")

    def log_message(self, message):
        """Helper function to print log messages."""
        print(f"[YouTubeWatcher] {message}")
