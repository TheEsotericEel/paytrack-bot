# PayTrackBot - Quick Start Guide

**Get your bot running in 5 minutes**

---

## Step 1: Create Telegram Bot (2 minutes)

1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Choose a name: `PayTrackBot`
4. Choose a username: `your_paytrack_bot` (must end in 'bot')
5. Copy the token that looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

---

## Step 2: Configure Environment (1 minute)

```bash
cd PayTrackBot
cp .env.example .env
nano .env
```

Paste your bot token:
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

Save and exit (Ctrl+X, Y, Enter)

---

## Step 3: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

Or if you have multiple Python versions:
```bash
pip3 install -r requirements.txt
```

---

## Step 4: Run the Bot (1 minute)

```bash
python bot.py
```

You should see:
```
✅ Database initialized
🚀 PayTrackBot started!
```

---

## Step 5: Test It! (30 seconds)

1. Open Telegram
2. Search for your bot username (e.g., `@your_paytrack_bot`)
3. Click Start
4. You should get a welcome message!
5. Try: `/new` to create your first invoice

---

## ✅ You're Done!

**The bot is now running locally.**

### Next Steps:

**For Testing:**
- Keep terminal open (bot is running)
- Try all commands: `/list`, `/stats`, `/help`
- Create a test invoice with `/new`

**For Production:**
- See `DEPLOYMENT.md` for systemd setup (keeps bot running 24/7)
- See `MARKETING.md` for getting your first users
- Run `python status.py` to see current stats

**For Reminders:**
- Set up cron job (see DEPLOYMENT.md section "Autonomous Reminders")
- Test with: `python reminders.py`

---

## Troubleshooting

**"ImportError: No module named 'telegram'"**
→ Run: `pip install python-telegram-bot==20.7`

**"401 Unauthorized"**
→ Check your bot token in `.env` file

**"Database locked"**
→ Only run one instance of `bot.py` at a time

**Bot not responding**
→ Make sure `bot.py` is still running (check terminal)

---

## Quick Commands Reference

- `/start` - Welcome message
- `/new` - Create invoice
- `/list` - View unpaid invoices
- `/stats` - Revenue stats
- `/paid <id>` - Mark invoice as paid
- `/help` - Full command list

---

**That's it! You have a working invoice tracker bot.**

Now go get some users! 🚀
