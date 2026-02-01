# PayTrackBot 📊

**Dead-simple invoice & payment tracker for freelancers**

Never miss a payment again. Track clients, invoices, and get automated reminders - all in Telegram.

## Features

### Free Tier
- ✅ Track up to 3 unpaid invoices
- ✅ Manual payment tracking
- ✅ Basic revenue statistics

### Pro Tier ($7/month)
- ✅ Unlimited invoices
- 🔔 Automated daily payment reminders
- 📊 Advanced revenue reports
- 💾 CSV export
- 📧 Email notifications

## Setup

### 1. Prerequisites
- Python 3.9+
- Telegram account
- (Optional) Stripe account for payments

### 2. Installation

```bash
cd PayTrackBot
pip install -r requirements.txt
```

### 3. Configuration

1. Create a bot with [@BotFather](https://t.me/botfather)
2. Copy `.env.example` to `.env`
3. Add your bot token to `.env`:

```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 4. Run the Bot

```bash
python bot.py
```

The bot will:
- Initialize the SQLite database
- Start listening for commands
- Be ready to track invoices!

## Usage

### Basic Commands

- `/start` - Welcome message & tutorial
- `/new` - Create new invoice (guided conversation)
- `/list` - View unpaid invoices with due dates
- `/all` - View all invoices (last 50)
- `/paid <id>` - Mark invoice as paid
- `/stats` - Revenue statistics
- `/help` - Full command list

### Creating an Invoice

```
You: /new
Bot: What's the client's name?
You: Acme Corp
Bot: What's the invoice amount?
You: 1500
Bot: When is it due? (Format: YYYY-MM-DD or 'today', '7d', '30d')
You: 30d
Bot: Add notes? (Optional) Type /skip to skip notes.
You: Website redesign project
Bot: ✅ Invoice Created! #12 Acme Corp, $1500.00, Due: 2026-03-03
```

### Checking Status

```
You: /list
Bot: 📋 Unpaid Invoices:

#12 Acme Corp
  💵 USD 1500.00 | 🟢 Due in 29 days

#11 TechStart LLC
  💵 USD 750.00 | 🔴 Due TODAY

💡 Use /paid <id> to mark as paid
```

### Marking as Paid

```
You: /paid 11
Bot: ✅ Invoice Marked Paid!
#11 TechStart LLC
💵 USD 750.00
Great job getting paid! 🎉
```

## Automated Reminders (Pro Only)

The bot sends daily reminders at 9 AM for:
- **Overdue invoices** - Past due date
- **Due today** - Invoice due today
- **Due tomorrow** - Invoice due in 1 day
- **Coming soon** - Invoices due in 3-7 days

### Setup Cron Job (Linux/Mac)

```bash
crontab -e
```

Add this line to run reminders daily at 9 AM:

```
0 9 * * * cd /path/to/PayTrackBot && python reminders.py >> logs/reminders.log 2>&1
```

### Setup Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start a program
   - Program: `C:\Python39\python.exe`
   - Arguments: `C:\path\to\PayTrackBot\reminders.py`

## Database Schema

**SQLite Database:** `data/paytrack.db`

### Tables

**users**
- telegram_id (PRIMARY KEY)
- username
- first_name
- subscription_tier (free/pro)
- subscription_expires
- stripe_customer_id
- created_at

**invoices**
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- client_name
- amount
- currency
- due_date
- status (unpaid/paid)
- paid_date
- notes
- created_at

**reminders**
- id (PRIMARY KEY)
- invoice_id (FOREIGN KEY)
- sent_at
- reminder_type

## Monetization

### Stripe Integration

1. Create a Stripe account at https://stripe.com
2. Create a product "PayTrackBot Pro" at $7/month
3. Get the Price ID (starts with `price_`)
4. Add to `.env`:

```
STRIPE_API_KEY=sk_live_your_key
STRIPE_PRICE_ID_PRO=price_1234567890
```

5. Set up webhook endpoint for subscription events
6. Update bot with payment link

### Telegram Stars (Alternative)

Telegram is rolling out native payments with Stars. Once available, update the `/upgrade` command with:

```python
await update.message.send_invoice(
    title="PayTrackBot Pro",
    description="Unlimited invoices + auto-reminders",
    payload="pro_monthly",
    provider_token="",  # Empty for Stars
    currency="XTR",
    prices=[LabeledPrice("Pro Subscription", 700)]  # 700 Stars = ~$7
)
```

## Deployment

### Option 1: Local Machine
- Run `python bot.py` in background
- Set up cron/Task Scheduler for reminders
- Use systemd or PM2 for auto-restart

### Option 2: VPS (Recommended)
- Deploy to DigitalOcean ($5/month) or AWS EC2
- Use systemd service for auto-start
- Nginx reverse proxy for webhooks (optional)

### Option 3: Railway/Render (Easiest)
- Connect GitHub repo
- Set environment variables
- Auto-deploys on push

### Systemd Service (Linux)

```ini
[Unit]
Description=PayTrackBot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/PayTrackBot
ExecStart=/usr/bin/python3 /path/to/PayTrackBot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable paytrackbot
sudo systemctl start paytrackbot
```

## Security Notes

- Never commit `.env` file to git
- Use `TELEGRAM_BOT_TOKEN` as environment variable in production
- Rotate Stripe keys if compromised
- SQLite database is local - backup regularly
- Consider encryption for sensitive invoice data

## Roadmap

- [ ] CSV export functionality
- [ ] Email notifications
- [ ] Multi-currency support (beyond USD)
- [ ] Recurring invoices
- [ ] Invoice templates
- [ ] Client payment history
- [ ] Expense tracking
- [ ] Profit/loss reports
- [ ] API integrations (Stripe, PayPal)
- [ ] Team collaboration features

## Support

- **Telegram:** @YourSupportUsername
- **Email:** support@yourdomain.com
- **GitHub Issues:** https://github.com/yourusername/PayTrackBot

## License

MIT License - feel free to modify and use for your own projects!

## Contributing

Pull requests welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Test thoroughly
4. Submit PR with description

---

Made with ❤️ for freelancers who hate chasing payments
