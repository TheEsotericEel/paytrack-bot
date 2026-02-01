"""Database management for PayTrackBot"""
import sqlite3
import os
from datetime import datetime, date
from typing import List, Dict, Optional
import config

def init_db():
    """Initialize database with schema"""
    # Create data directory if it doesn't exist
    db_dir = os.path.dirname(config.DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            subscription_tier TEXT DEFAULT 'free',
            subscription_expires TIMESTAMP,
            stripe_customer_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            client_name TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            due_date DATE NOT NULL,
            status TEXT DEFAULT 'unpaid',
            paid_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id)
        )
    ''')
    
    # Reminders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reminder_type TEXT NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[OK] Database initialized")

def get_user(telegram_id: int) -> Optional[Dict]:
    """Get user by Telegram ID"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def create_user(telegram_id: int, username: str = None, first_name: str = None) -> Dict:
    """Create new user"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (telegram_id, username, first_name)
        VALUES (?, ?, ?)
    ''', (telegram_id, username, first_name))
    
    conn.commit()
    conn.close()
    
    return get_user(telegram_id)

def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None) -> Dict:
    """Get existing user or create new one"""
    user = get_user(telegram_id)
    if not user:
        user = create_user(telegram_id, username, first_name)
    return user

def create_invoice(user_id: int, client_name: str, amount: float, 
                   due_date: date, currency: str = 'USD', notes: str = None) -> int:
    """Create new invoice and return ID"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO invoices (user_id, client_name, amount, currency, due_date, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, client_name, amount, currency, due_date, notes))
    
    invoice_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return invoice_id

def get_unpaid_invoices(user_id: int) -> List[Dict]:
    """Get all unpaid invoices for user"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM invoices 
        WHERE user_id = ? AND status = 'unpaid'
        ORDER BY due_date ASC
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_all_invoices(user_id: int, limit: int = 50) -> List[Dict]:
    """Get all invoices for user (paid and unpaid)"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM invoices 
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def mark_invoice_paid(invoice_id: int, paid_date: date = None) -> bool:
    """Mark invoice as paid"""
    if paid_date is None:
        paid_date = date.today()
    
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE invoices 
        SET status = 'paid', paid_date = ?
        WHERE id = ?
    ''', (paid_date, invoice_id))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success

def delete_invoice(invoice_id: int, user_id: int) -> bool:
    """Delete invoice (only if belongs to user)"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM invoices 
        WHERE id = ? AND user_id = ?
    ''', (invoice_id, user_id))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success

def get_invoice(invoice_id: int) -> Optional[Dict]:
    """Get invoice by ID"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM invoices WHERE id = ?', (invoice_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def count_unpaid_invoices(user_id: int) -> int:
    """Count unpaid invoices for user"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM invoices 
        WHERE user_id = ? AND status = 'unpaid'
    ''', (user_id,))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count

def get_revenue_stats(user_id: int, period: str = 'month') -> Dict:
    """Get revenue statistics for user"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # This month's paid invoices
    cursor.execute('''
        SELECT SUM(amount) as total, COUNT(*) as count
        FROM invoices
        WHERE user_id = ? 
        AND status = 'paid'
        AND strftime('%Y-%m', paid_date) = strftime('%Y-%m', 'now')
    ''', (user_id,))
    
    month_data = cursor.fetchone()
    
    # All time stats
    cursor.execute('''
        SELECT SUM(amount) as total, COUNT(*) as count
        FROM invoices
        WHERE user_id = ? AND status = 'paid'
    ''', (user_id,))
    
    all_time_data = cursor.fetchone()
    
    # Outstanding amount
    cursor.execute('''
        SELECT SUM(amount) as total
        FROM invoices
        WHERE user_id = ? AND status = 'unpaid'
    ''', (user_id,))
    
    outstanding = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'month_total': month_data[0] or 0,
        'month_count': month_data[1] or 0,
        'all_time_total': all_time_data[0] or 0,
        'all_time_count': all_time_data[1] or 0,
        'outstanding': outstanding
    }

def update_user_subscription(telegram_id: int, tier: str, expires: datetime = None, 
                             stripe_customer_id: str = None):
    """Update user subscription tier"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET subscription_tier = ?, 
            subscription_expires = ?,
            stripe_customer_id = COALESCE(?, stripe_customer_id)
        WHERE telegram_id = ?
    ''', (tier, expires, stripe_customer_id, telegram_id))
    
    conn.commit()
    conn.close()

def log_reminder(invoice_id: int, reminder_type: str):
    """Log that a reminder was sent"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO reminders (invoice_id, reminder_type)
        VALUES (?, ?)
    ''', (invoice_id, reminder_type))
    
    conn.commit()
    conn.close()

def get_all_users_for_reminders() -> List[int]:
    """Get all user IDs who have unpaid invoices for reminder checking"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT user_id 
        FROM invoices 
        WHERE status = 'unpaid'
    ''')
    
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return user_ids
