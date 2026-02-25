"""
Database module for EmoRecs - SQLite backend
Handles user authentication, data storage, and admin functions
"""
import sqlite3
import bcrypt
import os
from datetime import datetime

# Database file path
DB_PATH = "emorecs.db"

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table - Create if not exists to preserve existing data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User activity/logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Emotion detection logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            detected_emotion TEXT NOT NULL,
            confidence REAL,
            recommendation_type TEXT,
            recommendation_item TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def register_user(username, email, password):
    """
    Register a new user with hashed password
    Returns: (success: bool, message: str)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists!"
        
        # Check if email already exists
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Email already registered!"
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert new user
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )
        user_id = cursor.lastrowid
        
        # Log the registration activity
        cursor.execute(
            "INSERT INTO user_activity (user_id, action, details) VALUES (?, ?, ?)",
            (user_id, "register", f"User registered: {username}")
        )
        
        conn.commit()
        conn.close()
        
        return True, "Account created successfully!"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def login_user(email, password):
    """
    Authenticate user with email and password
    Returns: (success: bool, user_data: dict or None, message: str)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user by email
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False, None, "Email not found!"
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Log the login activity
            cursor.execute(
                "INSERT INTO user_activity (user_id, action, details) VALUES (?, ?, ?)",
                (user['id'], "login", f"User logged in: {user['username']}")
            )
            conn.commit()
            conn.close()
            
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at']
            }
            return True, user_data, "Login successful!"
        else:
            conn.close()
            return False, None, "Incorrect password!"
            
    except Exception as e:
        return False, None, f"Error: {str(e)}"

def log_emotion_detection(user_id, emotion, confidence, recommendation_type=None, recommendation_item=None):
    """Log emotion detection results"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO emotion_logs 
               (user_id, detected_emotion, confidence, recommendation_type, recommendation_item) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, emotion, confidence, recommendation_type, recommendation_item)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error logging emotion: {e}")
        return False

def get_all_users():
    """Get all registered users (for admin view)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, created_at 
            FROM users 
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in users]
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

def get_user_activity(user_id=None):
    """Get user activity logs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute("""
                SELECT ua.*, u.username 
                FROM user_activity ua
                JOIN users u ON ua.user_id = u.id
                WHERE ua.user_id = ?
                ORDER BY ua.timestamp DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT ua.*, u.username 
                FROM user_activity ua
                JOIN users u ON ua.user_id = u.id
                ORDER BY ua.timestamp DESC
            """)
        
        activities = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in activities]
    except Exception as e:
        print(f"Error getting activity: {e}")
        return []

def get_emotion_logs(user_id=None):
    """Get emotion detection logs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute("""
                SELECT el.*, u.username 
                FROM emotion_logs el
                JOIN users u ON el.user_id = u.id
                WHERE el.user_id = ?
                ORDER BY el.timestamp DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT el.*, u.username 
                FROM emotion_logs el
                JOIN users u ON el.user_id = u.id
                ORDER BY el.timestamp DESC
            """)
        
        logs = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in logs]
    except Exception as e:
        print(f"Error getting emotion logs: {e}")
        return []

def get_database_stats():
    """Get database statistics for admin view"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()[0]
        
        # Total activities
        cursor.execute("SELECT COUNT(*) FROM user_activity")
        stats['total_activities'] = cursor.fetchone()[0]
        
        # Total emotion logs
        cursor.execute("SELECT COUNT(*) FROM emotion_logs")
        stats['total_emotion_logs'] = cursor.fetchone()[0]
        
        # Recent registrations (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE created_at >= datetime('now', '-7 days')
        """)
        stats['new_users_7days'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {}

def delete_user(user_id):
    """Delete a user and their data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete related records first
        cursor.execute("DELETE FROM emotion_logs WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM user_activity WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        return True, "User deleted successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

# Initialize database on module import
init_db()
