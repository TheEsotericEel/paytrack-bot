"""Configuration for PayTrackBot"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token (get from @BotFather)
TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN', '')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set. Please set it before running the bot.")

# Stripe API Key (for subscription payments)
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY', '')
STRIPE_PRICE_ID_PRO = os.getenv('STRIPE_PRICE_ID_PRO', '')  # $7/month price ID

# Database path
DB_PATH = 'data/paytrack.db'

# Subscription tiers
TIER_FREE = 'free'
TIER_PRO = 'pro'

# Free tier limits
FREE_TIER_MAX_INVOICES = 3

# Reminder times (24-hour format)
REMINDER_TIME_HOUR = 9  # 9 AM daily check
REMINDER_TIME_MINUTE = 0

# Currency options
DEFAULT_CURRENCY = 'USD'
SUPPORTED_CURRENCIES = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']
