# PayTrackBot Launch Checklist

**Copy this to track your progress**

---

## Phase 1: Setup (30 minutes)

### Create Bot
- [ ] Message @BotFather on Telegram
- [ ] Send `/newbot`
- [ ] Choose name: `PayTrackBot`
- [ ] Choose username: `[your]_paytrack_bot`
- [ ] Copy bot token
- [ ] Save token somewhere safe

### Configure Environment
- [ ] Navigate to `PayTrackBot` folder
- [ ] Copy `.env.example` to `.env`
- [ ] Add your bot token to `.env`
- [ ] (Optional) Add Stripe keys for payments

### Install & Test
- [ ] Run `pip install -r requirements.txt`
- [ ] Run `python test_bot.py` (should pass all tests)
- [ ] Run `python bot.py` (start bot locally)
- [ ] Open Telegram, search for your bot
- [ ] Send `/start` - should get welcome message
- [ ] Try `/new` - create a test invoice
- [ ] Try `/list` - see your invoice
- [ ] Try `/paid 1` - mark it as paid
- [ ] Try `/stats` - see revenue stats
- [ ] **If all works: ✅ Bot is functional!**

---

## Phase 2: Deploy to Production (30 minutes)

### Set Up Server (if not already running)
- [ ] Have a Linux VPS (DigitalOcean, AWS, etc.)
- [ ] SSH access configured
- [ ] Python 3.9+ installed
- [ ] Git installed (optional, for code transfer)

### Deploy Bot
- [ ] Transfer code to server (scp, git clone, etc.)
- [ ] Install dependencies: `pip3 install -r requirements.txt`
- [ ] Add `.env` file with bot token
- [ ] Test run: `python3 bot.py`
- [ ] Verify bot responds in Telegram

### Make It Persistent (Systemd)
- [ ] Create service file: `/etc/systemd/system/paytrackbot.service`
- [ ] Copy template from DEPLOYMENT.md
- [ ] Update paths in service file
- [ ] Run `sudo systemctl daemon-reload`
- [ ] Run `sudo systemctl enable paytrackbot`
- [ ] Run `sudo systemctl start paytrackbot`
- [ ] Check status: `sudo systemctl status paytrackbot`
- [ ] **If running: ✅ Bot is live 24/7!**

### Set Up Automated Reminders
- [ ] Create logs directory: `mkdir -p logs`
- [ ] Edit crontab: `crontab -e`
- [ ] Add cron job from DEPLOYMENT.md (daily 9 AM)
- [ ] Test manually: `python3 reminders.py`
- [ ] **If works: ✅ Reminders configured!**

---

## Phase 3: Launch Marketing (Week 1-2)

### Reddit Launch
- [ ] Read r/freelance rules (no spam!)
- [ ] Write post using template from MARKETING.md
- [ ] Include demo video or screenshots
- [ ] Post in r/freelance
- [ ] Post in r/webdev
- [ ] Post in r/forhire
- [ ] Post in r/SideProject
- [ ] Respond to ALL comments
- [ ] **Track signups in spreadsheet**

### Product Hunt Prep
- [ ] Create Product Hunt account
- [ ] Write tagline: "Never miss a freelance payment again"
- [ ] Record 2-min demo video (Loom)
- [ ] Take 3-5 screenshots
- [ ] Write description
- [ ] Prepare for launch day

### Product Hunt Launch
- [ ] Launch on Tuesday, Wednesday, or Thursday
- [ ] Post at 12:01 AM PST for full day exposure
- [ ] Ask 5 friends to upvote/comment early
- [ ] Respond to ALL comments quickly
- [ ] Share on Twitter, LinkedIn
- [ ] Post in Indie Hackers
- [ ] **Goal: Top 10 of the day**

---

## Phase 4: Monitor & Optimize (Ongoing)

### Daily Checks (5 minutes)
- [ ] Check bot status: `systemctl status paytrackbot`
- [ ] Quick stats: `python status.py`
- [ ] Review any error logs
- [ ] Respond to user questions

### Weekly Tasks (30 minutes)
- [ ] Check user growth metrics
- [ ] Review free → pro conversion rate
- [ ] Read user feedback
- [ ] Backup database
- [ ] Plan next marketing push

### Monthly Tasks (2 hours)
- [ ] Calculate MRR (Monthly Recurring Revenue)
- [ ] Review churn rate
- [ ] Add most-requested features
- [ ] Write blog post / Twitter thread with updates
- [ ] Update roadmap

---

## Success Metrics Tracker

### Week 2
- [ ] 50 total users
- [ ] 3 Pro users ($21 MRR)
- [ ] Product Hunt launch complete

### Month 1
- [ ] 150 total users
- [ ] 10 Pro users ($70 MRR)
- [ ] Break-even on costs

### Month 3
- [ ] 500 total users
- [ ] 50 Pro users ($350 MRR)
- [ ] 10% free → pro conversion

### Month 6
- [ ] 1,000 total users
- [ ] 100 Pro users ($700 MRR)
- [ ] Profitable!

---

## Optional: Stripe Payment Setup

### Create Stripe Account
- [ ] Sign up at stripe.com
- [ ] Complete business verification
- [ ] Create product: "PayTrackBot Pro"
- [ ] Set price: $7/month
- [ ] Get Price ID (starts with `price_`)
- [ ] Add to `.env` file

### Update Bot
- [ ] Add Stripe API key to config
- [ ] Test `/upgrade` command
- [ ] Create payment link
- [ ] Test subscription flow

---

## Troubleshooting

**Bot not responding?**
- [ ] Check if running: `systemctl status paytrackbot`
- [ ] Check logs: `journalctl -u paytrackbot -n 50`
- [ ] Restart: `sudo systemctl restart paytrackbot`

**Reminders not sending?**
- [ ] Test manually: `python3 reminders.py`
- [ ] Check cron logs: `grep CRON /var/log/syslog`
- [ ] Verify cron syntax

**Database errors?**
- [ ] Check permissions: `ls -la data/`
- [ ] Verify SQLite installed: `sqlite3 --version`
- [ ] Kill zombie processes: `pkill -f bot.py`

---

## Quick Reference Commands

```bash
# Start bot locally
python bot.py

# Run tests
python test_bot.py

# Check status
python status.py
systemctl status paytrackbot

# View logs
journalctl -u paytrackbot -n 50
tail -f logs/reminders.log

# Restart bot
sudo systemctl restart paytrackbot

# Backup database
cp data/paytrack.db backups/paytrack_$(date +%Y%m%d).db

# Test reminders
python reminders.py
```

---

## 🎯 YOUR GOAL

**First 2 weeks:** Get 3 paying users ($21 MRR)

**Why this matters:**
- Validates product-market fit
- Covers server costs
- Proves concept works
- Builds momentum

**How to get there:**
1. Launch on Reddit (week 1)
2. Launch on Product Hunt (week 2)
3. Share on Twitter
4. DM 10 freelancer friends

**You got this! 🚀**

---

**Print this checklist and cross off items as you complete them.**

**Questions?** See MAIN_AGENT_SUMMARY.md or DEPLOYMENT.md
