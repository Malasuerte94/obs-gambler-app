import datetime
import time
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView

from tabs.youtube_watcher.youtube_chat import get_live_video_id, analyze_hot_message, analyze_top_messages
from tabs.youtube_watcher.youtube_helper import YouTubeChatTracker, UserActivityTable
from tabs.youtube_watcher.youtube_hot_word import update_hotword_html


class YouTubeWatcherTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.parent.log_status("Initializing YouTubeWatcherTab")
        self.ignored_users = [user.strip() for user in self.parent.settings.get('ignored_users', '').split(',') if
                              user.strip()]
        self.message_count = 0
        try:
            self.chat_tracker = YouTubeChatTracker(parent.settings)
            self.parent.log_status("Chat tracker initialized successfully")
        except Exception as e:
            self.parent.log_status(f"Failed to initialize chat tracker: {e}")
            self.parent.log_status(f"Error initializing database: {e}")
        self.seen_message_ids = set()
        self.last_hotword = None
        self.last_percent = None
        self.last_top3 = None
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)

        self.hotword_display = QtWidgets.QTextEdit()
        self.hotword_display.setReadOnly(True)
        self.hotword_display.setFixedHeight(80)
        self.hotword_display.setFixedWidth(200)
        self.hotword_display.setStyleSheet("font-size: 10pt; background-color: #222; color: white;")
        self.hotword_display.setText("HOT-WORDS: N/A")

        self.top3_checkbox = QtWidgets.QCheckBox("TOP 3")
        self.top3_checkbox.setStyleSheet("font-size: 9pt;")

        self.active_users_label = QtWidgets.QLabel("Active Users: 0")
        self.active_users_label.setAlignment(QtCore.Qt.AlignCenter)
        self.active_users_label.setStyleSheet("font-size: 9pt;")

        self.message_count_label = QtWidgets.QLabel("Messages: 0 added")
        self.message_count_label.setAlignment(QtCore.Qt.AlignCenter)
        self.message_count_label.setStyleSheet("font-size: 9pt;")

        self.timeout_label = QtWidgets.QLabel(f"Timeout: {int(self.parent.settings.get('chat_interval', 1))} minutes")
        self.timeout_label.setAlignment(QtCore.Qt.AlignCenter)
        self.timeout_label.setStyleSheet("font-size: 9pt;")

        self.ignored_label = QtWidgets.QLabel(
            f"Ignored: {', '.join(self.ignored_users)}")
        self.ignored_label.setAlignment(QtCore.Qt.AlignCenter)
        self.ignored_label.setWordWrap(True)
        self.ignored_label.setStyleSheet("font-size: 9pt;")

        self.points_countdown_label = QtWidgets.QLabel("Points Update in: 00:00")
        self.points_countdown_label.setAlignment(QtCore.Qt.AlignCenter)
        self.points_countdown_label.setStyleSheet("font-size: 9pt;")

        self.add_points_layout = QtWidgets.QHBoxLayout()
        self.points_input = QtWidgets.QLineEdit()
        self.points_input.setPlaceholderText("Points")
        self.points_input.setFixedWidth(80)

        self.add_points_button = QtWidgets.QPushButton("Add to All")
        self.add_points_button.clicked.connect(self.add_points_to_all)

        self.add_points_layout.addWidget(self.points_input)
        self.add_points_layout.addWidget(self.add_points_button)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setContentsMargins(2, 2, 2, 2)
        left_layout.setSpacing(4)
        left_layout.addWidget(self.hotword_display)
        left_layout.addWidget(self.top3_checkbox)
        left_layout.addWidget(self.active_users_label)
        left_layout.addWidget(self.message_count_label)
        left_layout.addWidget(self.timeout_label)
        left_layout.addWidget(self.ignored_label)
        left_layout.addWidget(self.points_countdown_label)
        left_layout.addLayout(self.add_points_layout)
        left_layout.addStretch()

        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(left_layout)
        self.splitter.addWidget(left_widget)

        try:
            self.user_activity_table = UserActivityTable()
            self.user_activity_table.set_tracker(self.chat_tracker)
            self.splitter.addWidget(self.user_activity_table)
            self.parent.log_status("User activity table initialized successfully")
        except Exception as e:
            self.parent.log_status(f"Failed to initialize user activity table: {e}", exc_info=True)
            self.parent.log_status(f"Error setting up user activity table: {e}")

        self.chat_view = QWebEngineView()
        self.chat_view.setZoomFactor(0.8)
        self.splitter.addWidget(self.chat_view)

        self.splitter.setSizes([200, 250, 800])

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(self.splitter)

        self.stats_timer = QtCore.QTimer(self)
        self.stats_timer.timeout.connect(self.update_user_stats)
        self.stats_timer.start(1000)

        self.parent.log_status("YouTubeWatcherTab initialization complete")
        self.load_settings()

    def update_user_stats(self):
        try:
            active_count = self.chat_tracker.get_active_count()
            self.active_users_label.setText(f"Active Users: {active_count}")

            current_time = int(time.time())
            last_award_time = int(self.chat_tracker.last_points_award_time)
            interval = int(self.chat_tracker.points_award_interval)

            seconds_left = max(0, (last_award_time + interval) - current_time)
            minutes = seconds_left // 60
            seconds = seconds_left % 60

            self.points_countdown_label.setText(f"Points Update in: {minutes:02d}:{seconds:02d}")
        except Exception as e:
            self.parent.log_status(f"Error updating user stats: {e}", exc_info=True)

    def add_points_to_all(self):
        try:
            points_text = self.points_input.text().strip()
            if not points_text or not points_text.isdigit():
                self.parent.log_status("Please enter a valid number of points")
                return

            points = int(points_text)
            success = self.chat_tracker.award_points_to_active_users(force=True, custom_points=points)

            if success:
                self.parent.log_status(f"Successfully added {points} points to all active users")
                self.points_input.clear()
            else:
                self.parent.log_status("Failed to add points to users")
        except Exception as e:
            self.parent.log_status(f"Error adding points: {e}")

    def onChatLoadFinished(self, ok):
        if ok:
            self.parent.log_status("Chat page loaded successfully")
            self.parent.log_status("Chat page loaded successfully. Starting extraction...")
            self.chat_timer = QtCore.QTimer(self)
            self.chat_timer.timeout.connect(self.extractChatMessages)
            self.chat_timer.start(1000)
        else:
            self.parent.log_status("Failed to load chat page")
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
        try:
            self.chat_view.page().runJavaScript(js_extract, self.handleChatMessages)
        except Exception as e:
            self.parent.log_status(f"Error executing JavaScript for chat extraction: {e}", exc_info=True)
            self.parent.log_status(f"Error extracting chat: {e}")

    def handleChatMessages(self, result):
        try:
            if result is not None:
                new_msgs = result.split("\n")
                new_msg_count = 0
                self.ignored_users = [user.strip() for user in self.parent.settings.get('ignored_users', '').split(',')
                                      if user.strip()]
                for msg in new_msgs:
                    parts = msg.split("||")
                    if len(parts) == 4:
                        msg_id, user, message, member_status = parts
                        if user in self.ignored_users:
                            continue
                        if msg_id not in self.seen_message_ids:
                            self.seen_message_ids.add(msg_id)
                            self.process_message(msg_id, user, message, member_status)
                            new_msg_count += 1
                if new_msg_count > 0:
                    self.message_count += new_msg_count
                    self.message_count_label.setText(f"Messages: {self.message_count} added")
                    self.parent.log_status(f"Added {new_msg_count} new messages")
                self.update_hotwords()
            else:
                self.parent.log_status("No chat messages extracted")
                self.parent.log_status("No chat messages extracted.")
        except Exception as e:
            self.parent.log_status(f"Error handling chat messages: {e}", exc_info=True)
            self.parent.log_status(f"Error processing chat messages: {e}")

    def process_message(self, msg_id, user, message, member_status):
        try:
            if user in self.ignored_users:
                return False
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            success = self.chat_tracker.add_message(msg_id, user, message, member_status, timestamp)
            if not success:
                self.parent.log_status(f"Failed to add message to database: {msg_id}")
                return False
            return True
        except Exception as e:
            self.parent.log_status(f"Error processing message: {e}", exc_info=True)
            self.parent.log_status(f"Error processing message: {e}")
            return False

    def update_hotwords(self):
        try:
            messages = []
            all_messages = self.chat_tracker.get_all_messages(limit=100)
            for _, _, message, _, _ in all_messages:
                if message and message.strip():
                    messages.append(message.strip())

            if len(messages) < 30:
                self.hotword_display.setText("HOT-WORDS: Not enough data")
                self.parent.log_status("Not enough messages for hotword analysis")
                return

            if self.top3_checkbox.isChecked():
                top3 = analyze_top_messages(messages, top_n=3)
                if top3:
                    hot_words_text = "HOT-WORDS (TOP 3):\n"
                    for idx, (word, percent) in enumerate(top3):
                        hot_words_text += f"{idx + 1}. {word} ({percent:.1f}%)\n"

                    self.hotword_display.setText(hot_words_text)
                    update_hotword_html(None, None, top3=top3)
                    self.parent.log_status("Updated TOP 3 hotwords")
                else:
                    self.hotword_display.setText("HOT-WORDS: N/A")
            else:
                hotword, percent = analyze_hot_message(messages)
                if hotword:
                    self.hotword_display.setText(f"HOT-WORD:\n{hotword.upper()}\n{percent:.1f}%")
                    update_hotword_html(hotword, percent)
                else:
                    self.hotword_display.setText("HOT-WORD: N/A")
        except Exception as e:
            self.parent.log_status(f"Error updating hotwords: {e}")
            self.parent.log_status(f"Error updating hotwords: {e}")

    def load_settings(self):
        self.parent.log_status("Loading Youtube Watcher settings")
        try:
            self.ignored_users = [user.strip() for user in self.parent.settings.get('ignored_users', '').split(',') if
                                  user.strip()]
            self.ignored_label.setText(f"Ignored: {', '.join(self.ignored_users)}")
            youtube_api = self.parent.settings.get("youtube_api", "")
            yt_channel = self.parent.settings.get("yt_channel", "")
            self.parent.log_status(f"Checking live stream for channel: {yt_channel}")
            self.parent.log_status("Resetting database for new session")
            self.chat_tracker.reset_database()
            self.seen_message_ids.clear()
            self.message_count = 0
            self.message_count_label.setText("Messages: 0 added")
            live_video_id = get_live_video_id(yt_channel, youtube_api)
            if live_video_id:
                self.parent.log_status(f"Live video found: {live_video_id}")
                chat_url = "https://www.youtube.com/live_chat?v=" + live_video_id
                self.parent.log_status("Loading chat URL: " + chat_url)
                self.chat_view.setUrl(QtCore.QUrl(chat_url))
                self.chat_view.loadFinished.connect(self.onChatLoadFinished)
            else:
                self.parent.log_status("No live video currently streaming")
        except Exception as e:
            self.parent.log_status("Error while checking live status: " + str(e))