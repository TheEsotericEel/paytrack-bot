"""Quick status check for PayTrackBot"""
import sqlite3
from datetime import datetime
import config

def get_bot_status():
    """Get current bot statistics"""
    stats = {
        'total_users': 0,
        'pro_users': 0,
        'free_users': 0,
        'total_invoices': 0,
        'unpaid_invoices': 0,
        'paid_this_month': 0,
        'revenue_this_month': 0,
        'db_size_mb': 0
    }
    
    try:
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
        
        # User counts
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_tier='pro'")
        stats['pro_users'] = cursor.fetchone()[0]
        stats['free_users'] = stats['total_users'] - stats['pro_users']
        
        # Invoice counts
        cursor.execute("SELECT COUNT(*) FROM invoices")
        stats['total_invoices'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoices WHERE status='unpaid'")
        stats['unpaid_invoices'] = cursor.fetchone()[0]
        
        # This month's paid invoices
        cursor.execute("""
            SELECT COUNT(*), SUM(amount) FROM invoices 
            WHERE status='paid' 
            AND strftime('%Y-%m', paid_date) = strftime('%Y-%m', 'now')
        """)
        month_data = cursor.fetchone()
        stats['paid_this_month'] = month_data[0] or 0
        stats['revenue_this_month'] = month_data[1] or 0
        
        conn.close()
        
        # Database size
        import os
        if os.path.exists(config.DB_PATH):
            stats['db_size_mb'] = os.path.getsize(config.DB_PATH) / (1024 * 1024)
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return None
    
    return stats

def print_status():
    """Print formatted status"""
    stats = get_bot_status()
    
    if not stats:
        print("❌ Could not retrieve status")
        return
    
    print("\n" + "="*50)
    print("📊 PayTrackBot Status - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
    print("="*50)
    
    print("\n👥 Users:")
    print(f"  Total: {stats['total_users']}")
    print(f"  Pro: {stats['pro_users']} (${stats['pro_users'] * 7}/month MRR)")
    print(f"  Free: {stats['free_users']}")
    
    print("\n📋 Invoices:")
    print(f"  Total created: {stats['total_invoices']}")
    print(f"  Currently unpaid: {stats['unpaid_invoices']}")
    print(f"  Paid this month: {stats['paid_this_month']}")
    
    print("\n💰 Revenue Tracked:")
    print(f"  This month: ${stats['revenue_this_month']:.2f}")
    
    print("\n💾 Database:")
    print(f"  Size: {stats['db_size_mb']:.2f} MB")
    
    print("\n" + "="*50 + "\n")

if __name__ == '__main__':
    print_status()
