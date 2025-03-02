import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from config.settings_manager import SettingsManager
from tabs.dashboard_tab import DashboardTab
from tabs.casino_manager_tab import CasinoManagerTab
from tabs.settings_tab import SettingsTab
from tabs.youtube_watcher_tab import YouTubeWatcherTab
from utils.logger import Logger


class CustomTitleBar(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setFixedHeight(40)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)

        self.title_label = QtWidgets.QLabel("Gambler Settings", self)
        self.title_label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(self.title_label)

        layout.addStretch()

        self.minimize_button = QtWidgets.QPushButton("—", self)
        self.minimize_button.setFixedSize(40, 30)
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        self.minimize_button.setStyleSheet(self.button_style())

        self.close_button = QtWidgets.QPushButton("✕", self)
        self.close_button.setFixedSize(40, 30)
        self.close_button.clicked.connect(self.parent.close)
        self.close_button.setStyleSheet(self.button_style())

        layout.addWidget(self.minimize_button)
        layout.addWidget(self.close_button)

    def button_style(self):
        return """
            QPushButton {
                background-color: #444;
                border: none;
                font-size: 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """


class GamblerSettingsApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet(self.dark_theme())
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.setGeometry(100, 100, 1270, 600)

        self.settings_manager = SettingsManager("settings.json")
        self.settings = self.settings_manager.load()

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QtWidgets.QVBoxLayout(self.central_widget)
        layout.setContentsMargins(10, 5, 10, 5)

        self.title_bar = CustomTitleBar(self)
        layout.addWidget(self.title_bar)

        self.status_log = Logger()

        self.tab_control = QtWidgets.QTabWidget()
        layout.addWidget(self.tab_control)

        self.dashboard_tab = DashboardTab(self)
        self.casino_manager_tab = CasinoManagerTab(self)
        self.youtube_watcher_tab = YouTubeWatcherTab(self)
        self.settings_tab = SettingsTab(self)

        self.tab_control.addTab(self.dashboard_tab, 'Dashboard')
        self.tab_control.addTab(self.casino_manager_tab, 'Casino Manager')
        self.tab_control.addTab(self.youtube_watcher_tab, 'YouTube Watcher')
        self.tab_control.addTab(self.settings_tab, 'Settings')
        layout.addWidget(self.status_log)

        self.drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos is not None:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def log_status(self, message):
        self.status_log.append_message(message)

    def dark_theme(self):
        return """
        QWidget {
            background-color: #222;
            color: white;
        }
        QTabWidget::pane {
            border: 1px solid #444;
        }
        QTabBar::tab {
            background: #333;
            padding: 10px;
        }
        QTabBar::tab:selected {
            background: #555;
        }
        QTextEdit {
            background: #333;
            color: white;
            border: 1px solid #444;
        }
        QPushButton {
            background: #444;
            border: none;
            padding: 8px;
            color: white;
        }
        QPushButton:hover {
            background: #666;
        }
        QLineEdit {
            background: #333;
            border: 1px solid #555;
            padding: 4px;
            color: white;
        }
        QComboBox {
            background: #333;
            border: 1px solid #555;
            padding: 4px;
            color: white;
        }
        QLabel {
            color: white;
        }
        """


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GamblerSettingsApp()
    window.show()
    sys.exit(app.exec_())