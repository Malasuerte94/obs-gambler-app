import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView

from tabs.youtube_watcher.youtube_chat import get_live_video_id, analyze_hotword, analyze_top_words
from tabs.youtube_watcher.youtube_hot_word import update_hotword_html


class YouTubeWatcherTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Maintain chat history (up to 1000 messages).
        self.chat_history = []
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

        # Middle pane: Chat log.
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.splitter.addWidget(self.log)

        # Right pane: Chat webpage.
        self.chat_view = QWebEngineView()
        self.splitter.addWidget(self.chat_view)

        self.splitter.setSizes([150, 300, 800])
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.splitter)

    def load_settings(self, youtube_api, yt_channel):
        """
        Update the settings for YouTubeWatcherTab.
        This method takes a YouTube API key and a channel ID,
        uses the helper function get_live_video_id to retrieve the live video ID,
        and then loads the corresponding live chat URL.
        """
        self.youtube_api = youtube_api
        self.yt_channel = yt_channel
        self.log.append("Checking for live stream on channel: " + yt_channel)
        try:
            live_video_id = get_live_video_id(yt_channel, youtube_api)
            if live_video_id:
                self.log.append("Live video found: " + live_video_id)
                chat_url = "https://www.youtube.com/live_chat?v=" + live_video_id
                self.log.append("Loading chat URL: " + chat_url)
                self.chat_view.setUrl(QtCore.QUrl(chat_url))
                self.chat_view.loadFinished.connect(self.onChatLoadFinished)
            else:
                self.log.append("No live video is currently streaming.")
        except Exception as e:
            self.log.append("Error while checking live status: " + str(e))

    def onChatLoadFinished(self, ok):
        if ok:
            self.log.append("Chat page loaded successfully. Starting extraction...")
            self.chat_timer = QtCore.QTimer(self)
            self.chat_timer.timeout.connect(self.extractChatMessages)
            self.chat_timer.start(1000)
        else:
            self.log.append("Failed to load chat page.")

    def extractChatMessages(self):
        js_extract = """
        (function(){
            var messages = [];
            var chatElements = document.querySelectorAll("yt-live-chat-text-message-renderer");
            for (var i = 0; i < chatElements.length; i++) {
                var messageElem = chatElements[i].querySelector("#message");
                var msg = messageElem ? messageElem.innerText.trim() : "";
                messages.push(msg);
            }
            messages.reverse();
            return messages.join("\\n");
        })();
        """
        self.chat_view.page().runJavaScript(js_extract, self.handleChatMessages)

    def handleChatMessages(self, result):
        if result is not None:
            self.log.setPlainText(result)
            new_msgs = result.split("\n")
            self.chat_history.extend(new_msgs)
            if len(self.chat_history) > 1000:
                self.chat_history = self.chat_history[-1000:]

            if self.top3_checkbox.isChecked():
                top3 = analyze_top_words(self.chat_history, top_n=3)
                if top3:
                    self.hotword_label.setText("HOT-WORD: (TOP 3)")
                    if top3 != self.last_top3:
                        update_hotword_html(None, None, top3=top3)
                        self.last_top3 = top3
                else:
                    self.hotword_label.setText("HOT-WORD: N/A")
            else:
                hotword, percent = analyze_hotword(self.chat_history)
                if hotword is not None:
                    self.hotword_label.setText(f"HOT-WORD: {hotword.upper()} {percent:.1f}%")
                else:
                    self.hotword_label.setText("HOT-WORD: N/A")
                if hotword != self.last_hotword or abs(percent - (self.last_percent or 0)) > 0.1:
                    update_hotword_html(hotword, percent)
                    self.last_hotword = hotword
                    self.last_percent = percent
        else:
            self.log.append("No chat messages extracted.")
