import sqlite3
import logging
from config import DB_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_file=DB_NAME):
        self.db_file = db_file
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_file)

    def init_db(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        first_name TEXT,
                        username TEXT,
                        phone TEXT,
                        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        flower_name TEXT,
                        color TEXT,
                        quantity INTEGER,
                        total_price INTEGER,
                        status TEXT DEFAULT 'Yangi',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                conn.commit()
                logger.info("Ma'lumotlar bazasi muvaffaqiyatli ishga tushdi.")
        except Exception as e:
            logger.error(f"Baza yaratishda xatolik: {e}")

    def add_user(self, user_id, first_name, username, phone=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (user_id, first_name, username, phone)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    first_name=excluded.first_name,
                    username=excluded.username,
                    phone=COALESCE(excluded.phone, users.phone)
            ''', (user_id, first_name, username, phone))
            conn.commit()

    def add_order(self, user_id, flower_name, color, quantity, total_price):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (user_id, flower_name, color, quantity, total_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, flower_name, color, quantity, total_price))
            conn.commit()
            return cursor.lastrowid

    def get_user_orders(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT order_id, flower_name, color, quantity, total_price, status, created_at
                FROM orders WHERE user_id = ? ORDER BY order_id DESC LIMIT 5
            ''', (user_id,))
            return cursor.fetchall()

    def get_stats(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*), COALESCE(SUM(total_price), 0) FROM orders')
            total_orders, total_revenue = cursor.fetchone()
            
            return total_users, total_orders, total_revenue
		