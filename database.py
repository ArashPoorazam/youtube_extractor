import sqlite3
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)
DB_NAME = 'bot_users.db'

def init_db():
    """Initializes the SQLite database and creates the users table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                join_time TEXT
            )
        """)
        conn.commit()
        conn.close()
        logger.info(f"Database {DB_NAME} initialized and 'users' table ensured.")
    except sqlite3.Error as e:
        logger.error(f"SQLite error during initialization: {e}")

def add_or_update_user(user_id: int, first_name: str, last_name: Optional[str], username: Optional[str]):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Check if the user already exists
        cursor.execute("SELECT join_time FROM users WHERE user_id = ?", (user_id,))
        existing_user = cursor.fetchone()

        # Sanitize data (convert None to empty string for database)
        last_name_sane = last_name or ''
        username_sane = username or ''

        if existing_user:
            # User exists: Update name/username (in case they changed it)
            cursor.execute("""
                UPDATE users SET
                    first_name = ?,
                    last_name = ?,
                    username = ?
                WHERE user_id = ?
            """, (first_name, last_name_sane, username_sane, user_id))
            logger.info(f"User {user_id} updated.")
        else:
            # User is new: Insert new record with current time
            join_time = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO users (user_id, first_name, last_name, username, join_time)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, first_name, last_name_sane, username_sane, join_time))
            logger.info(f"New user {user_id} added at {join_time}.")
            
        conn.commit()
        conn.close()
        
    except sqlite3.Error as e:
        logger.error(f"SQLite error during user data handling for user {user_id}: {e}")