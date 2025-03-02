import sqlite3
import time
import datetime
import os
import logging

from utils.api_client import APIClient
from utils.api_points import award_points

LOG_FILE = 'youtube_helper.log'
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='youtube_helper.log',
    filemode='a'
)

logger = logging.getLogger('YouTubeHelper')
DB_FILE = "youtube_chat.db"

class YouTubeChatTracker:
    def __init__(self, settings, db_file=DB_FILE):
        self.settings = settings
        self.api_client = APIClient(settings)
        self.inactive_timeout = int(self.settings.get('chat_interval', 1)) * 60
        self.db_file = db_file
        self.last_points_award_time = 0
        self.points_award_interval = self.inactive_timeout
        self.conn = None
        self.cursor = None
        self.reset_database()

    def reset_database(self):
        logger.info(f"Creating fresh database: {self.db_file}")
        try:
            if self.conn:
                self.conn.close()
            if os.path.exists(self.db_file):
                os.remove(self.db_file)
                logger.info(f"Removed existing database file: {self.db_file}")
            self.initialize_db()
        except Exception as e:
            logger.error(f"Error resetting database: {e}", exc_info=True)
            raise

    def initialize_db(self):
        logger.info(f"Initializing database: {self.db_file}")
        try:
            db_dir = os.path.dirname(self.db_file)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                logger.info(f"Created database directory: {db_dir}")
            self.conn = sqlite3.connect(self.db_file)
            logger.debug("Database connection established")
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    message TEXT,
                    is_member INTEGER,
                    timestamp TEXT
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    last_activity REAL,
                    is_active INTEGER,
                    message_count INTEGER,
                    is_member INTEGER
                )
            ''')
            self.conn.commit()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}", exc_info=True)
            raise

    def add_message(self, message_id, user_id, message, is_member, timestamp=None):
        if user_id in self.settings.get('ignored_users', '').split(','):
            logger.debug(f"Ignoring message from {user_id} (in ignored users list)")
            return True
        logger.debug(f"Adding message from {user_id}: {message[:20]}...")
        try:
            if timestamp is None:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            is_member_int = 1 if is_member == "Yes" else 0
            self.cursor.execute(
                "INSERT OR IGNORE INTO messages VALUES (?, ?, ?, ?, ?)",
                (message_id, user_id, message, is_member_int, timestamp)
            )
            if self.cursor.rowcount > 0:
                logger.debug(f"Message {message_id} inserted")
                current_time = time.time()
                self.cursor.execute(
                    "SELECT message_count FROM users WHERE user_id = ?",
                    (user_id,)
                )
                result = self.cursor.fetchone()
                if result is None:
                    logger.info(f"New user detected: {user_id}")
                    self.cursor.execute(
                        "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                        (user_id, current_time, 1, 1, is_member_int)
                    )
                else:
                    message_count = result[0] + 1
                    self.cursor.execute(
                        "UPDATE users SET last_activity = ?, is_active = 1, message_count = ?, is_member = ? WHERE user_id = ?",
                        (current_time, message_count, is_member_int, user_id)
                    )
                    logger.debug(f"Updated user {user_id}, message count: {message_count}")
            else:
                logger.debug(f"Message {message_id} already exists, skipped")
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding message: {e}", exc_info=True)
            return False

    def process_timeouts(self):
        logger.debug("Processing timeouts")
        try:
            current_time = time.time()
            threshold = current_time - self.inactive_timeout
            self.cursor.execute(
                "SELECT user_id FROM users WHERE is_active = 1 AND last_activity < ?",
                (threshold,)
            )
            inactive_users = [row[0] for row in self.cursor.fetchall()]
            if inactive_users:
                logger.info(f"Marking {len(inactive_users)} users as inactive: {', '.join(inactive_users[:5])}...")
                placeholders = ','.join(['?'] * len(inactive_users))
                self.cursor.execute(
                    f"UPDATE users SET is_active = 0 WHERE user_id IN ({placeholders})",
                    inactive_users
                )
                self.conn.commit()
            return inactive_users
        except Exception as e:
            logger.error(f"Error processing timeouts: {e}", exc_info=True)
            return []

    def award_points_to_active_users(self, force=False):
        points = int(self.settings.get('chat_points', 1))
        try:
            current_time = time.time()
            time_since_last_award = current_time - self.last_points_award_time

            # Check if we should award points based on time interval
            if not force and time_since_last_award < self.points_award_interval:
                logger.debug(
                    f"Skipping points award - next award in {self.points_award_interval - time_since_last_award:.1f} seconds")
                return False

            active_users = self.get_active_users()
            if not active_users:
                logger.info("No active users to award points")
                return False

            user_ids = [user[0] for user in active_users]
            logger.info(f"Awarding {points} points to {len(user_ids)} active users")

            result = award_points(user_ids, points, self.settings.get('streamer_id'), self.api_client)

            if result:
                # Update the last award time only if successful
                self.last_points_award_time = current_time

            return result

        except Exception as e:
            logger.error(f"Error awarding points to active users: {e}", exc_info=True)
            return False

    def get_active_users(self):
        logger.debug("Getting active users")
        try:
            self.process_timeouts()
            self.cursor.execute(
                "SELECT user_id, last_activity, message_count, is_member FROM users WHERE is_active = 1"
            )
            users = self.cursor.fetchall()
            logger.debug(f"Found {len(users)} active users")
            return users
        except Exception as e:
            logger.error(f"Error getting active users: {e}", exc_info=True)
            return []

    def get_inactive_users(self):
        logger.debug("Getting inactive users")
        try:
            self.process_timeouts()
            self.cursor.execute(
                "SELECT user_id, last_activity, message_count, is_member FROM users WHERE is_active = 0"
            )
            users = self.cursor.fetchall()
            logger.debug(f"Found {len(users)} inactive users")
            return users
        except Exception as e:
            logger.error(f"Error getting inactive users: {e}", exc_info=True)
            return []

    def get_all_messages(self, limit=1000):
        logger.debug(f"Getting all messages (limit: {limit})")
        try:
            self.cursor.execute(
                "SELECT message_id, user_id, message, is_member, timestamp FROM messages ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting messages: {e}", exc_info=True)
            return []

    def get_active_count(self):
        logger.debug("Getting active user count")
        try:
            self.process_timeouts()
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            count = self.cursor.fetchone()[0]
            logger.debug(f"Active user count: {count}")
            return count
        except Exception as e:
            logger.error(f"Error getting active count: {e}", exc_info=True)
            return 0

    def get_total_users(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM users")
            return self.cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting total users: {e}", exc_info=True)
            return 0

    def shutdown(self):
        logger.info("Shutting down database connection")
        if self.conn:
            try:
                self.conn.commit()
                self.conn.close()
                logger.info("Database connection closed properly")
            except Exception as e:
                logger.error(f"Error shutting down database: {e}", exc_info=True)


from PyQt5 import QtWidgets, QtCore, QtGui


class UserActivityTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Initializing UserActivityTable")
        self.tracker = None
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Status", "User", "Msgs", "Last Active"])
        self.setColumnWidth(0, 40)
        self.setColumnWidth(1, 120)
        self.setColumnWidth(2, 50)
        self.setColumnWidth(3, 120)
        self.verticalHeader().setDefaultSectionSize(20)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setStyleSheet("""
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
        self.update_timer = QtCore.QTimer(self)
        self.update_timer.timeout.connect(self.update_user_list)
        self.update_timer.start(10000)
        logger.info("UserActivityTable initialized")

    def set_tracker(self, tracker):
        logger.info("Setting tracker for UserActivityTable")
        self.tracker = tracker
        self.update_user_list()

    def update_user_list(self):
        logger.debug("Updating user activity table")
        if not self.tracker:
            logger.warning("No tracker set for UserActivityTable")
            return
        try:
            self.tracker.process_timeouts()
            active_users = self.tracker.get_active_users()
            inactive_users = self.tracker.get_inactive_users()
            logger.debug(f"Updating table with {len(active_users)} active and {len(inactive_users)} inactive users")
            self.setRowCount(0)
            for i, (user_id, last_activity, msg_count, is_member) in enumerate(active_users):
                self.insertRow(i)
                status_item = QtWidgets.QTableWidgetItem()
                status_item.setBackground(QtGui.QColor(0, 200, 0))
                self.setItem(i, 0, status_item)
                self.setItem(i, 1, QtWidgets.QTableWidgetItem(str(user_id)))
                self.setItem(i, 2, QtWidgets.QTableWidgetItem(str(msg_count)))
                timestamp = datetime.datetime.fromtimestamp(last_activity).strftime("%H:%M:%S")
                self.setItem(i, 3, QtWidgets.QTableWidgetItem(timestamp))
            row_count = len(active_users)
            for j, (user_id, last_activity, msg_count, is_member) in enumerate(inactive_users):
                row = row_count + j
                self.insertRow(row)
                status_item = QtWidgets.QTableWidgetItem()
                status_item.setBackground(QtGui.QColor(200, 0, 0))
                self.setItem(row, 0, status_item)
                self.setItem(row, 1, QtWidgets.QTableWidgetItem(str(user_id)))
                self.setItem(row, 2, QtWidgets.QTableWidgetItem(str(msg_count)))
                timestamp = datetime.datetime.fromtimestamp(last_activity).strftime("%H:%M:%S")
                self.setItem(row, 3, QtWidgets.QTableWidgetItem(timestamp))
            logger.debug("User activity table updated successfully")

            self.tracker.award_points_to_active_users()
        except Exception as e:
            logger.error(f"Error updating user list: {e}", exc_info=True)