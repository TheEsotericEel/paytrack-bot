"""Test suite for PayTrackBot"""
import sqlite3
from datetime import date, timedelta
import database as db
import config

def setup_test_db():
    """Create test database"""
    config.DB_PATH = 'data/test_paytrack.db'
    db.init_db()
    print("[OK] Test database initialized")

def test_user_creation():
    """Test creating users"""
    print("\nTesting user creation...")
    
    user1 = db.create_user(telegram_id=12345, username="testuser", first_name="Test")
    assert user1['telegram_id'] == 12345
    assert user1['subscription_tier'] == 'free'
    print("[OK] User creation works")
    
    # Test get_or_create
    user2 = db.get_or_create_user(12345)
    assert user2['telegram_id'] == 12345
    print("[OK] Get or create works")

def test_invoice_creation():
    """Test creating invoices"""
    print("\nTesting invoice creation...")
    
    user = db.get_or_create_user(12345, "testuser", "Test")
    
    invoice_id = db.create_invoice(
        user_id=12345,
        client_name="Acme Corp",
        amount=1500.00,
        due_date=date.today() + timedelta(days=30),
        notes="Test invoice"
    )
    
    assert invoice_id > 0
    print(f"[OK] Invoice created with ID {invoice_id}")
    
    invoice = db.get_invoice(invoice_id)
    assert invoice['client_name'] == "Acme Corp"
    assert invoice['amount'] == 1500.00
    print("[OK] Invoice retrieval works")

def test_invoice_listing():
    """Test listing invoices"""
    print("\nTesting invoice listing...")
    
    # Create multiple invoices
    today = date.today()
    
    db.create_invoice(12345, "Client A", 500, today + timedelta(days=5))
    db.create_invoice(12345, "Client B", 750, today + timedelta(days=15))
    db.create_invoice(12345, "Client C", 1000, today - timedelta(days=5))  # Overdue
    
    unpaid = db.get_unpaid_invoices(12345)
    assert len(unpaid) >= 3
    print(f"[OK] Found {len(unpaid)} unpaid invoices")
    
    all_invoices = db.get_all_invoices(12345)
    assert len(all_invoices) >= 3
    print(f"[OK] All invoices: {len(all_invoices)}")

def test_mark_paid():
    """Test marking invoices as paid"""
    print("\nTesting mark as paid...")
    
    invoice_id = db.create_invoice(12345, "Test Client", 300, date.today())
    
    success = db.mark_invoice_paid(invoice_id)
    assert success
    
    invoice = db.get_invoice(invoice_id)
    assert invoice['status'] == 'paid'
    assert invoice['paid_date'] is not None
    print("[OK] Mark as paid works")

def test_revenue_stats():
    """Test revenue statistics"""
    print("\nTesting revenue stats...")
    
    # Create and mark some as paid
    inv1 = db.create_invoice(12345, "Paid Client", 1000, date.today())
    db.mark_invoice_paid(inv1)
    
    stats = db.get_revenue_stats(12345)
    assert stats['month_total'] > 0
    assert stats['month_count'] > 0
    print(f"[OK] Revenue stats: ${stats['month_total']:.2f} this month")

def test_subscription_limits():
    """Test free tier limits"""
    print("\nTesting subscription limits...")
    
    user = db.get_user(12345)
    count = db.count_unpaid_invoices(12345)
    
    print(f"  User tier: {user['subscription_tier']}")
    print(f"  Unpaid invoices: {count}")
    print(f"  Free tier limit: {config.FREE_TIER_MAX_INVOICES}")
    
    if count > config.FREE_TIER_MAX_INVOICES:
        print("[WARN] Would trigger upgrade prompt")
    else:
        print("[OK] Within free tier limits")

def cleanup_test_db():
    """Remove test database"""
    import os
    if os.path.exists('data/test_paytrack.db'):
        os.remove('data/test_paytrack.db')
        print("\n[CLEAN] Test database removed")

def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("PayTrackBot Test Suite")
    print("="*50)
    
    setup_test_db()
    
    try:
        test_user_creation()
        test_invoice_creation()
        test_invoice_listing()
        test_mark_paid()
        test_revenue_stats()
        test_subscription_limits()
        
        print("\n" + "="*50)
        print("[OK] All tests passed!")
        print("="*50)
        
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
    finally:
        cleanup_test_db()

if __name__ == '__main__':
    run_all_tests()
