# PayTrackBot Deployment Guide

**For Main Agent: How to deploy and manage PayTrackBot autonomously**

## Quick Start (5 minutes)

### 1. Create the Telegram Bot

```bash
# Message @BotFather on Telegram
/newbot
# Name: PayTrackBot
# Username: your_paytrack_bot (must end in 'bot')
# Copy the token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 2. Set Up Environment

```bash
cd PayTrackBot
cp .env.example .env
nano .env  # Add your bot token
```

Example `.env`:
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
STRIPE_API_KEY=sk_test_51...
STRIPE_PRICE_ID_PRO=price_1...
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Test Run

```bash
python bot.py
```

Open Telegram, search for your bot, send `/start`. If it responds, you're good!

## Production Deployment

### Option A: Run as Background Service (Recommended)

**Linux/Mac (systemd):**

1. Create service file:
```bash
sudo nano /etc/systemd/system/paytrackbot.service
```

```ini
[Unit]
Description=PayTrackBot - Invoice Tracker
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/clawd/PayTrackBot
ExecStart=/usr/bin/python3 /home/your_username/clawd/PayTrackBot/bot.py
Restart=always
RestartSec=10

Environment="TELEGRAM_BOT_TOKEN=your_token_here"

[Install]
WantedBy=multi-user.target
```

2. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable paytrackbot
sudo systemctl start paytrackbot
sudo systemctl status paytrackbot
```

**Windows (Task Scheduler):**

1. Open Task Scheduler
2. Create Basic Task: "PayTrackBot"
3. Trigger: At startup
4. Action: Start a program
   - Program: `C:\Python39\python.exe`
   - Arguments: `C:\Users\Joe\clawd\PayTrackBot\bot.py`
   - Start in: `C:\Users\Joe\clawd\PayTrackBot`

### Option B: Run with PM2 (Node.js required)

```bash
npm install -g pm2
cd PayTrackBot
pm2 start bot.py --name paytrackbot --interpreter python3
pm2 save
pm2 startup
```

## Autonomous Reminders (Cron Setup)

The bot sends automated payment reminders to Pro users daily.

### Linux/Mac Cron

```bash
crontab -e
```

Add this line (runs daily at 9 AM):
```
0 9 * * * cd /home/username/clawd/PayTrackBot && /usr/bin/python3 reminders.py >> logs/reminders.log 2>&1
```

Create logs directory:
```bash
mkdir -p PayTrackBot/logs
```

### Windows Task Scheduler

1. Create Basic Task: "PayTrackBot Reminders"
2. Trigger: Daily at 9:00 AM
3. Action: Start a program
   - Program: `C:\Python39\python.exe`
   - Arguments: `C:\Users\Joe\clawd\PayTrackBot\reminders.py`

## Main Agent Management Tasks

### Daily Checks (via Heartbeat)

**What to monitor:**
- Is the bot running? `systemctl status paytrackbot` or `pm2 status paytrackbot`
- Any errors in logs? `journalctl -u paytrackbot -n 50` or `pm2 logs paytrackbot`
- Database size growing? `ls -lh data/paytrack.db`

**Automation script:**
```bash
#!/bin/bash
# check_paytrackbot.sh

# Check if bot is running
if ! systemctl is-active --quiet paytrackbot; then
    echo "⚠️ PayTrackBot is down! Restarting..."
    systemctl start paytrackbot
    # Send alert to owner
fi

# Check log for errors
if grep -q "ERROR" /var/log/paytrackbot.log; then
    echo "⚠️ Errors detected in PayTrackBot logs"
    tail -n 20 /var/log/paytrackbot.log
fi
```

Add to cron:
```
*/30 * * * * /home/username/clawd/PayTrackBot/check_paytrackbot.sh
```

### Weekly Tasks

**Database backup:**
```bash
#!/bin/bash
# backup_db.sh
DATE=$(date +%Y%m%d)
cp data/paytrack.db backups/paytrack_$DATE.db
# Keep only last 30 days
find backups/ -name "paytrack_*.db" -mtime +30 -delete
```

**User stats:**
```bash
sqlite3 data/paytrack.db "SELECT COUNT(*) FROM users;"
sqlite3 data/paytrack.db "SELECT COUNT(*) FROM users WHERE subscription_tier='pro';"
sqlite3 data/paytrack.db "SELECT COUNT(*) FROM invoices WHERE created_at > date('now', '-7 days');"
```

### Monthly Tasks

- Review user growth metrics
- Check Stripe subscription sync
- Update pricing if needed
- Review feature requests

## Monitoring Dashboard (Optional)

Create `status.py` for quick health check:

```python
import sqlite3
import config
import database as db
from datetime import datetime, timedelta

def get_bot_status():
    stats = {
        'total_users': 0,
        'pro_users': 0,
        'free_users': 0,
        'total_invoices': 0,
        'unpaid_invoices': 0,
        'revenue_this_month': 0
    }
    
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    stats['total_users'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_tier='pro'")
    stats['pro_users'] = cursor.fetchone()[0]
    stats['free_users'] = stats['total_users'] - stats['pro_users']
    
    cursor.execute("SELECT COUNT(*) FROM invoices")
    stats['total_invoices'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM invoices WHERE status='unpaid'")
    stats['unpaid_invoices'] = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT SUM(amount) FROM invoices 
        WHERE status='paid' 
        AND strftime('%Y-%m', paid_date) = strftime('%Y-%m', 'now')
    """)
    stats['revenue_this_month'] = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return stats

if __name__ == '__main__':
    stats = get_bot_status()
    print("📊 PayTrackBot Status")
    print(f"Users: {stats['total_users']} ({stats['pro_users']} Pro, {stats['free_users']} Free)")
    print(f"Invoices: {stats['total_invoices']} total, {stats['unpaid_invoices']} unpaid")
    print(f"Revenue tracked this month: ${stats['revenue_this_month']:.2f}")
```

Run with: `python status.py`

## Troubleshooting

### Bot not responding
```bash
# Check if running
systemctl status paytrackbot

# Check logs
journalctl -u paytrackbot -f

# Restart
sudo systemctl restart paytrackbot
```

### Reminders not sending
```bash
# Test manually
python reminders.py

# Check cron logs
grep CRON /var/log/syslog | grep paytrack

# Verify cron is running
systemctl status cron
```

### Database locked error
```bash
# Check for zombie processes
ps aux | grep bot.py

# Kill if needed
pkill -f bot.py

# Restart
systemctl start paytrackbot
```

## Scaling Strategy

### First 100 Users
- Single VPS ($5/month DigitalOcean droplet)
- SQLite database is fine
- Manual monitoring via heartbeat checks

### 100-1000 Users
- Upgrade to $10/month VPS (2GB RAM)
- Add database backups to S3/DO Spaces
- Set up Sentry for error tracking
- Add rate limiting

### 1000+ Users
- Migrate to PostgreSQL
- Load balancer + multiple bot instances
- Redis for caching
- Separate worker for reminders
- Professional monitoring (Datadog/New Relic)

## Cost Breakdown

**Infrastructure:**
- VPS: $5-10/month (DigitalOcean, Hetzner, AWS Lightsail)
- Domain: $10/year (optional, for payment webhook)
- Stripe fees: 2.9% + $0.30 per transaction
- Total: ~$7-15/month

**Revenue Projection (Conservative):**
- 10 Pro users × $7/month = $70/month
- 50 Pro users × $7/month = $350/month
- 100 Pro users × $7/month = $700/month

**Break-even: ~2-3 Pro subscribers**

## Next Steps

1. ✅ Bot is running
2. ✅ Cron job set up for reminders
3. 🔲 Set up Stripe payment links
4. 🔲 Create landing page (optional)
5. 🔲 Start marketing (Reddit, Product Hunt)
6. 🔲 Monitor user growth
7. 🔲 Collect feedback & iterate

---

**Questions?** Check README.md or ping the main agent!
