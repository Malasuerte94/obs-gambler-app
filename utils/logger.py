from PyQt5 import QtWidgets
from PyQt5.QtCore import QDateTime


class Logger(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFixedHeight(100)

    def append_message(self, message):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.append(f"[{timestamp}] {message}")
