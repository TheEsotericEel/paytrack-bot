"""Automated reminder system for PayTrackBot"""
import asyncio
from datetime import date, timedelta
from telegram import Bot
from telegram.error import TelegramError
import config
import database as db
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def send_daily_reminders():
    """Send daily reminder notifications to users with due/overdue invoices"""
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    user_ids = db.get_all_users_for_reminders()
    logger.info(f"Checking reminders for {len(user_ids)} users...")
    
    reminders_sent = 0
    
    for user_id in user_ids:
        user = db.get_user(user_id)
        
        # Only send auto-reminders to Pro users
        if user['subscription_tier'] != config.TIER_PRO:
            continue
        
        invoices = db.get_unpaid_invoices(user_id)
        
        # Group invoices by urgency
        overdue = []
        due_today = []
        due_tomorrow = []
        due_soon = []  # 3-7 days
        
        for inv in invoices:
            due_date = date.fromisoformat(inv['due_date'])
            days_until = (due_date - today).days
            
            if days_until < 0:
                overdue.append((inv, abs(days_until)))
            elif days_until == 0:
                due_today.append(inv)
            elif days_until == 1:
                due_tomorrow.append(inv)
            elif 3 <= days_until <= 7:
                due_soon.append(inv)
        
        # Build reminder message
        msg_parts = []
        
        if overdue:
            msg_parts.append("⚠️ **OVERDUE INVOICES:**")
            for inv, days in overdue:
                msg_parts.append(
                    f"• #{inv['id']} {inv['client_name']} - "
                    f"${inv['amount']:.2f} ({days} days overdue)"
                )
            db.log_reminder(inv['id'], 'overdue')
        
        if due_today:
            msg_parts.append("\n🔴 **DUE TODAY:**")
            for inv in due_today:
                msg_parts.append(
                    f"• #{inv['id']} {inv['client_name']} - ${inv['amount']:.2f}"
                )
            db.log_reminder(inv['id'], 'due_today')
        
        if due_tomorrow:
            msg_parts.append("\n🟡 **DUE TOMORROW:**")
            for inv in due_tomorrow:
                msg_parts.append(
                    f"• #{inv['id']} {inv['client_name']} - ${inv['amount']:.2f}"
                )
            db.log_reminder(inv['id'], 'due_tomorrow')
        
        if due_soon:
            msg_parts.append("\n📅 **Coming up soon:**")
            for inv in due_soon:
                due_date = date.fromisoformat(inv['due_date'])
                days = (due_date - today).days
                msg_parts.append(
                    f"• #{inv['id']} {inv['client_name']} - "
                    f"${inv['amount']:.2f} (in {days} days)"
                )
        
        # Only send if there's something to report
        if msg_parts:
            msg_parts.insert(0, "📊 **Daily Invoice Reminder**\n")
            msg_parts.append("\nUse /paid <id> to mark as paid!")
            
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text='\n'.join(msg_parts),
                    parse_mode='Markdown'
                )
                reminders_sent += 1
                logger.info(f"Sent reminder to user {user_id}")
            except TelegramError as e:
                logger.error(f"Failed to send reminder to {user_id}: {e}")
    
    logger.info(f"✅ Sent {reminders_sent} reminders")
    return reminders_sent

async def send_weekly_summary():
    """Send weekly revenue summary (optional feature)"""
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    
    # Get all Pro users
    # This would need a query to get all users with subscription_tier = 'pro'
    # For now, simplified version
    
    logger.info("Weekly summary feature - coming soon")
    return 0

def run_daily_reminders():
    """Run the daily reminder check (called by cron)"""
    asyncio.run(send_daily_reminders())

if __name__ == '__main__':
    # For testing
    print("Running daily reminders...")
    run_daily_reminders()
    print("Done!")
