import datetime
import logging
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView

from tabs.youtube_watcher.youtube_chat import get_live_video_id, analyze_hot_message, analyze_top_messages
from tabs.youtube_watcher.youtube_helper import YouTubeChatTracker, UserActivityTable
from tabs.youtube_watcher.youtube_hot_word import update_hotword_html

logger = logging.getLogger('YouTubeWatcher')

class YouTubeWatcherTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        logger.info("Initializing YouTubeWatcherTab")
        self.parent = parent
        self.ignored_users = self.parent.settings.get('ignored_users', '').split(',')
        try:
            self.chat_tracker = YouTubeChatTracker(parent.settings)
            logger.info("Chat tracker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize chat tracker: {e}", exc_info=True)
            self.parent.log_status(f"Error initializing database: {e}")
        self.seen_message_ids = set()
        self.last_hotword = None
        self.last_percent = None
        self.last_top3 = None
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        self.hotword_label = QtWidgets.QLabel("HOT-WORD: N/A")
        self.hotword_label.setAlignment(QtCore.Qt.AlignCenter)
        self.hotword_label.setFixedWidth(120)
        self.hotword_label.setStyleSheet("font-size: 9pt;")
        self.top3_checkbox = QtWidgets.QCheckBox("TOP 3")
        self.top3_checkbox.setStyleSheet("font-size: 9pt;")
        self.active_users_label = QtWidgets.QLabel("Active Users: 0")
        self.active_users_label.setAlignment(QtCore.Qt.AlignCenter)
        self.active_users_label.setStyleSheet("font-size: 9pt;")
        self.timeout_label = QtWidgets.QLabel(f"Timeout: {int(self.parent.settings.get('chat_interval', 1))} minutes")
        self.timeout_label.setAlignment(QtCore.Qt.AlignCenter)
        self.timeout_label.setStyleSheet("font-size: 9pt;")
        self.ignored_label = QtWidgets.QLabel(f"Ignored: {', '.join(self.parent.settings.get('ignored_users', '').split(','))}")
        self.ignored_label.setAlignment(QtCore.Qt.AlignCenter)
        self.ignored_label.setWordWrap(True)
        self.ignored_label.setStyleSheet("font-size: 9pt;")
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setContentsMargins(2, 2, 2, 2)
        left_layout.setSpacing(4)
        left_layout.addWidget(self.hotword_label)
        left_layout.addWidget(self.top3_checkbox)
        left_layout.addWidget(self.active_users_label)
        left_layout.addWidget(self.timeout_label)
        left_layout.addWidget(self.ignored_label)
        left_layout.addStretch()
        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(left_layout)
        self.splitter.addWidget(left_widget)
        self.chat_table = QtWidgets.QTableWidget()
        self.chat_table.setColumnCount(4)
        self.chat_table.setHorizontalHeaderLabels(["User", "Message", "Member", "Date-Time"])
        self.chat_table.setColumnWidth(0, 120)
        self.chat_table.setColumnWidth(1, 320)
        self.chat_table.setColumnWidth(2, 40)
        self.chat_table.setColumnWidth(3, 90)
        self.chat_table.verticalHeader().setDefaultSectionSize(20)
        self.chat_table.verticalHeader().setVisible(False)
        self.chat_table.setShowGrid(False)
        self.chat_table.setStyleSheet("""
               QTableWidget {
                   background-color: #222;
                   color: white;
                   gridline-color: #444;
                   selection-background-color: #444;
                   selection-color: white;
                   font-size: 9pt;
               }
               QHeaderView::section {
                   background-color: #333;
                   color: white;
                   padding: 2px;
                   border: 1px solid #444;
                   font-size: 9pt;
               }
               QTableCornerButton::section {
                   background-color: #333;
                   border: 1px solid #444;
               }
           """)
        self.splitter.addWidget(self.chat_table)
        try:
            self.user_activity_table = UserActivityTable()
            self.user_activity_table.set_tracker(self.chat_tracker)
            self.splitter.addWidget(self.user_activity_table)
            logger.info("User activity table initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize user activity table: {e}", exc_info=True)
            self.parent.log_status(f"Error setting up user activity table: {e}")
        self.chat_view = QWebEngineView()
        self.chat_view.setZoomFactor(0.8)
        self.chat_view.loadFinished.connect(self.apply_web_styles)
        self.splitter.addWidget(self.chat_view)
        self.splitter.setSizes([150, 350, 250, 800])
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(self.splitter)
        self.stats_timer = QtCore.QTimer(self)
        self.stats_timer.timeout.connect(self.update_user_stats)
        self.stats_timer.start(5000)
        logger.info("YouTubeWatcherTab initialization complete")
        self.load_settings()

    def apply_web_styles(self, success):
        if success:
            css = """
            * {
                font-size: 0.9em !important;
            }
            yt-live-chat-renderer {
                padding: 0 !important;
            }
            yt-live-chat-message-renderer, 
            yt-live-chat-text-message-renderer {
                padding: 2px 4px !important;
                min-height: 24px !important;
            }
            #author-photo {
                width: 20px !important;
                height: 20px !important;
            }
            #item-offset {
                padding-left: 24px !important;
            }
            """
            js = f"""
            (function() {{
                var style = document.createElement('style');
                style.type = 'text/css';
                style.innerHTML = `{css}`;
                document.head.appendChild(style);
                console.log('Applied custom CSS to YouTube chat');
            }})();
            """
            self.chat_view.page().runJavaScript(js)
            logger.info("Applied custom styles to YouTube chat")

    def update_user_stats(self):
        try:
            active_count = self.chat_tracker.get_active_count()
            self.active_users_label.setText(f"Active Users: {active_count}")
            logger.debug(f"Updated active users count: {active_count}")
        except Exception as e:
            logger.error(f"Error updating user stats: {e}", exc_info=True)

    def onChatLoadFinished(self, ok):
        if ok:
            logger.info("Chat page loaded successfully")
            self.parent.log_status("Chat page loaded successfully. Starting extraction...")
            self.chat_timer = QtCore.QTimer(self)
            self.chat_timer.timeout.connect(self.extractChatMessages)
            self.chat_timer.start(1000)
        else:
            logger.error("Failed to load chat page")
            self.parent.log_status("Failed to load chat page.")

    def extractChatMessages(self):
        logger.debug("Extracting chat messages")
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
            logger.error(f"Error executing JavaScript for chat extraction: {e}", exc_info=True)
            self.parent.log_status(f"Error extracting chat: {e}")

    def handleChatMessages(self, result):
        try:
            if result is not None:
                new_msgs = result.split("\n")
                new_msg_count = 0
                logger.debug(f"Processing {len(new_msgs)} potential messages")
                for msg in new_msgs:
                    parts = msg.split("||")
                    if len(parts) == 4:
                        msg_id, user, message, member_status = parts
                        if user in self.ignored_users:
                            continue
                        if msg_id not in self.seen_message_ids:
                            self.seen_message_ids.add(msg_id)
                            self.add_message_to_table(msg_id, user, message, member_status)
                            new_msg_count += 1
                if new_msg_count > 0:
                    logger.info(f"Added {new_msg_count} new messages")
                self.update_hotwords()
            else:
                logger.debug("No chat messages extracted")
                self.parent.log_status("No chat messages extracted.")
        except Exception as e:
            logger.error(f"Error handling chat messages: {e}", exc_info=True)
            self.parent.log_status(f"Error processing chat messages: {e}")

    def add_message_to_table(self, msg_id, user, message, member_status):
        try:
            if user in self.ignored_users:
                return
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            full_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            success = self.chat_tracker.add_message(msg_id, user, message, member_status, full_timestamp)
            if not success:
                logger.warning(f"Failed to add message to database: {msg_id}")
                return
            self.chat_table.insertRow(0)
            self.chat_table.setItem(0, 0, QtWidgets.QTableWidgetItem(user))
            self.chat_table.setItem(0, 1, QtWidgets.QTableWidgetItem(message))
            self.chat_table.setItem(0, 2, QtWidgets.QTableWidgetItem("Y" if member_status == "Yes" else "N"))
            self.chat_table.setItem(0, 3, QtWidgets.QTableWidgetItem(timestamp))
            while self.chat_table.rowCount() > 1000:
                self.chat_table.removeRow(1000)
            logger.debug(f"Added message from {user}: {message[:20]}...")
        except Exception as e:
            logger.error(f"Error adding message to table: {e}", exc_info=True)
            self.parent.log_status(f"Error adding message: {e}")

    def update_hotwords(self):
        try:
            max_messages = min(100, self.chat_table.rowCount())
            messages = [
                self.chat_table.item(row, 1).text().strip()
                for row in range(max_messages)
                if self.chat_table.item(row, 1) and self.chat_table.item(row, 1).text().strip()
            ]

            if len(messages) < 30:
                self.hotword_label.setText("HOT-WORD: Not enough data")
                logger.debug("Not enough messages for hotword analysis")
                return

            if not messages:
                self.hotword_label.setText("HOT-WORD: N/A")
                logger.debug("No messages for hotword analysis")
                return

            if self.top3_checkbox.isChecked():
                top3 = analyze_top_messages(messages, top_n=3)
                if top3:
                    self.hotword_label.setText(f"TOP 3: {', '.join([word for word, _ in top3])}")
                    update_hotword_html(None, None, top3=top3)
                    logger.info(f"Updated TOP 3 hotwords: {', '.join([word for word, _ in top3])}")
                else:
                    self.hotword_label.setText("HOT-WORD: N/A")
            else:
                hotword, percent = analyze_hot_message(messages)
                if hotword:
                    self.hotword_label.setText(f"HOT-WORD: {hotword.upper()} {percent:.1f}%")
                    update_hotword_html(hotword, percent)
                    logger.info(f"Updated hotword: {hotword.upper()} {percent:.1f}%")
                else:
                    self.hotword_label.setText("HOT-WORD: N/A")
        except IndexError as e:
            logger.error(f"Error updating hotwords: List index out of range - {e}", exc_info=True)
            self.parent.log_status(f"Error updating hotwords: List index out of range - {e}")
        except Exception as e:
            logger.error(f"Unexpected error in update_hotwords: {e}", exc_info=True)
            self.parent.log_status(f"Unexpected error in update_hotwords: {e}")

    def load_settings(self):
        logger.info("Loading Youtube Watcher settings")
        try:
            youtube_api = self.parent.settings.get("youtube_api", "")
            yt_channel = self.parent.settings.get("yt_channel", "")
            self.chat_table.setRowCount(0)
            self.parent.log_status("Checking for live stream on channel: " + yt_channel)
            logger.info(f"Checking live stream for channel: {yt_channel}")
            logger.info("Resetting database for new session")
            self.chat_tracker.reset_database()
            self.seen_message_ids.clear()
            live_video_id = get_live_video_id(yt_channel, youtube_api)
            if live_video_id:
                logger.info(f"Live video found: {live_video_id}")
                self.parent.log_status("Live video found: " + live_video_id)
                chat_url = "https://www.youtube.com/live_chat?v=" + live_video_id
                self.parent.log_status("Loading chat URL: " + chat_url)
                self.chat_view.setUrl(QtCore.QUrl(chat_url))
                self.chat_view.loadFinished.connect(self.onChatLoadFinished)
            else:
                logger.warning("No live video currently streaming")
                self.parent.log_status("No live video is currently streaming.")
        except Exception as e:
            logger.error(f"Error loading settings: {e}", exc_info=True)
            self.parent.log_status("Error while checking live status: " + str(e))