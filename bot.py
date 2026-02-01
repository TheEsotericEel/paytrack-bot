"""PayTrackBot - Telegram Invoice Tracker for Freelancers"""
import logging
from datetime import datetime, date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

import config
import database as db

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
CLIENT_NAME, AMOUNT, DUE_DATE, NOTES = range(4)

# === COMMAND HANDLERS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - welcome new users"""
    user = update.effective_user
    db_user = db.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    welcome_msg = f"""👋 Welcome to **PayTrackBot**, {user.first_name}!

I help freelancers track invoices and never miss a payment.

**Quick Commands:**
/new - Create a new invoice
/list - View all unpaid invoices
/stats - See your revenue stats
/help - Full command list

**Free Plan:** Track up to {config.FREE_TIER_MAX_INVOICES} unpaid invoices
**Pro Plan ($7/mo):** Unlimited invoices + auto-reminders

Let's track your first invoice! Use /new to get started.
"""
    
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    help_msg = """**PayTrackBot Commands**

**Invoice Management:**
/new - Create new invoice
/list - View unpaid invoices
/all - View all invoices (last 50)
/paid <id> - Mark invoice as paid
/delete <id> - Delete an invoice
/view <id> - View invoice details

**Statistics:**
/stats - Revenue statistics
/export - Export to CSV (Pro only)

**Account:**
/upgrade - Upgrade to Pro ($7/month)
/account - View subscription status
/help - This help message

**Need help?** Contact @YourSupportUsername
"""
    
    await update.message.reply_text(help_msg, parse_mode='Markdown')

async def list_invoices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all unpaid invoices"""
    user_id = update.effective_user.id
    invoices = db.get_unpaid_invoices(user_id)
    
    if not invoices:
        await update.message.reply_text("✅ No unpaid invoices! You're all caught up.")
        return
    
    today = date.today()
    msg_lines = ["**📋 Unpaid Invoices:**\n"]
    
    for inv in invoices:
        due = datetime.strptime(inv['due_date'], '%Y-%m-%d').date()
        days_diff = (due - today).days
        
        if days_diff < 0:
            status = f"⚠️ *OVERDUE by {abs(days_diff)} days*"
        elif days_diff == 0:
            status = "🔴 *Due TODAY*"
        elif days_diff <= 3:
            status = f"🟡 Due in {days_diff} days"
        else:
            status = f"🟢 Due in {days_diff} days"
        
        msg_lines.append(
            f"**#{inv['id']}** {inv['client_name']}\n"
            f"  💵 {inv['currency']} {inv['amount']:.2f} | {status}\n"
        )
    
    msg_lines.append(f"\n💡 Use `/paid <id>` to mark as paid")
    
    await update.message.reply_text('\n'.join(msg_lines), parse_mode='Markdown')

async def all_invoices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all invoices (paid and unpaid)"""
    user_id = update.effective_user.id
    invoices = db.get_all_invoices(user_id, limit=50)
    
    if not invoices:
        await update.message.reply_text("No invoices yet. Create one with /new")
        return
    
    msg_lines = ["**📊 All Invoices (Last 50):**\n"]
    
    for inv in invoices:
        status_emoji = "✅" if inv['status'] == 'paid' else "⏳"
        msg_lines.append(
            f"{status_emoji} **#{inv['id']}** {inv['client_name']} - "
            f"{inv['currency']} {inv['amount']:.2f}"
        )
    
    await update.message.reply_text('\n'.join(msg_lines), parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show revenue statistics"""
    user_id = update.effective_user.id
    stats = db.get_revenue_stats(user_id)
    
    stats_msg = f"""**📈 Your Revenue Stats**

**This Month:**
💰 ${stats['month_total']:.2f} earned
📝 {stats['month_count']} invoices paid

**All Time:**
💵 ${stats['all_time_total']:.2f} total
📋 {stats['all_time_count']} invoices

**Outstanding:**
⏳ ${stats['outstanding']:.2f} unpaid

Keep crushing it! 🚀
"""
    
    await update.message.reply_text(stats_msg, parse_mode='Markdown')

async def account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show account status"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    unpaid_count = db.count_unpaid_invoices(user_id)
    
    tier = user['subscription_tier'].upper()
    
    if user['subscription_tier'] == config.TIER_FREE:
        limit_msg = f"{unpaid_count}/{config.FREE_TIER_MAX_INVOICES} unpaid invoices"
        upgrade_msg = "\n💎 Upgrade to Pro for unlimited invoices! /upgrade"
    else:
        limit_msg = f"{unpaid_count} unpaid invoices (unlimited)"
        expires = user['subscription_expires']
        upgrade_msg = f"\n✅ Pro subscription active until {expires}"
    
    account_msg = f"""**👤 Your Account**

**Plan:** {tier}
**Invoices:** {limit_msg}
**Member since:** {user['created_at'][:10]}
{upgrade_msg}
"""
    
    await update.message.reply_text(account_msg, parse_mode='Markdown')

async def upgrade_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show upgrade options"""
    upgrade_msg = """**💎 Upgrade to Pro**

**Pro Features ($7/month):**
✅ Unlimited invoices
🔔 Auto payment reminders
📊 Advanced revenue reports
💾 CSV export
📧 Email notifications

**Payment Options:**
1. Telegram Stars (coming soon)
2. Stripe: [Subscribe Here](https://buy.stripe.com/your-link)

Questions? Contact @YourSupport
"""
    
    await update.message.reply_text(upgrade_msg, parse_mode='Markdown')

async def mark_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark invoice as paid: /paid <invoice_id>"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Usage: /paid <invoice_id>\nExample: /paid 5")
        return
    
    try:
        invoice_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid invoice ID. Must be a number.")
        return
    
    invoice = db.get_invoice(invoice_id)
    
    if not invoice:
        await update.message.reply_text("❌ Invoice not found.")
        return
    
    if invoice['user_id'] != user_id:
        await update.message.reply_text("❌ This invoice doesn't belong to you.")
        return
    
    if invoice['status'] == 'paid':
        await update.message.reply_text("✅ This invoice is already marked as paid!")
        return
    
    db.mark_invoice_paid(invoice_id)
    
    success_msg = f"""✅ **Invoice Marked Paid!**

**#{invoice_id}** {invoice['client_name']}
💵 {invoice['currency']} {invoice['amount']:.2f}

Great job getting paid! 🎉
"""
    
    await update.message.reply_text(success_msg, parse_mode='Markdown')

async def delete_invoice_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete invoice: /delete <invoice_id>"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Usage: /delete <invoice_id>\nExample: /delete 5")
        return
    
    try:
        invoice_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid invoice ID. Must be a number.")
        return
    
    success = db.delete_invoice(invoice_id, user_id)
    
    if success:
        await update.message.reply_text(f"🗑️ Invoice #{invoice_id} deleted.")
    else:
        await update.message.reply_text("❌ Invoice not found or doesn't belong to you.")

# === CONVERSATION HANDLER FOR CREATING INVOICE ===

async def new_invoice_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start new invoice conversation"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    # Check free tier limit
    if user['subscription_tier'] == config.TIER_FREE:
        unpaid_count = db.count_unpaid_invoices(user_id)
        if unpaid_count >= config.FREE_TIER_MAX_INVOICES:
            await update.message.reply_text(
                f"⚠️ Free plan limit reached ({config.FREE_TIER_MAX_INVOICES} unpaid invoices).\n\n"
                f"Mark some invoices as paid or upgrade to Pro: /upgrade"
            )
            return ConversationHandler.END
    
    await update.message.reply_text(
        "📝 **Create New Invoice**\n\n"
        "What's the client's name?\n\n"
        "(Send /cancel to abort)",
        parse_mode='Markdown'
    )
    
    return CLIENT_NAME

async def get_client_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save client name, ask for amount"""
    context.user_data['client_name'] = update.message.text
    
    await update.message.reply_text(
        f"✅ Client: **{update.message.text}**\n\n"
        f"What's the invoice amount?\n"
        f"(Example: 500 or 1250.50)",
        parse_mode='Markdown'
    )
    
    return AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save amount, ask for due date"""
    try:
        amount = float(update.message.text.replace(',', ''))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Please enter a valid positive number. Example: 500")
        return AMOUNT
    
    context.user_data['amount'] = amount
    
    await update.message.reply_text(
        f"✅ Amount: **${amount:.2f}**\n\n"
        f"When is it due?\n"
        f"(Format: YYYY-MM-DD or type 'today', '7d', '30d')\n"
        f"Example: 2026-03-01 or 30d",
        parse_mode='Markdown'
    )
    
    return DUE_DATE

async def get_due_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save due date, ask for notes"""
    text = update.message.text.strip().lower()
    
    try:
        if text == 'today':
            due_date = date.today()
        elif text.endswith('d') and text[:-1].isdigit():
            days = int(text[:-1])
            due_date = date.today() + timedelta(days=days)
        else:
            due_date = datetime.strptime(text, '%Y-%m-%d').date()
        
        if due_date < date.today() - timedelta(days=365):
            await update.message.reply_text("Due date seems too far in the past. Try again.")
            return DUE_DATE
            
    except ValueError:
        await update.message.reply_text(
            "Invalid date format. Use:\n"
            "- YYYY-MM-DD (e.g., 2026-03-01)\n"
            "- 'today'\n"
            "- '7d', '30d', etc."
        )
        return DUE_DATE
    
    context.user_data['due_date'] = due_date
    
    await update.message.reply_text(
        f"✅ Due: **{due_date}**\n\n"
        f"Add notes? (Optional)\n"
        f"Type /skip to skip notes.",
        parse_mode='Markdown'
    )
    
    return NOTES

async def get_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save notes and create invoice"""
    notes = update.message.text if update.message.text != '/skip' else None
    context.user_data['notes'] = notes
    
    return await create_invoice_final(update, context)

async def skip_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skip notes and create invoice"""
    context.user_data['notes'] = None
    return await create_invoice_final(update, context)

async def create_invoice_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Final step - create the invoice"""
    user_id = update.effective_user.id
    
    invoice_id = db.create_invoice(
        user_id=user_id,
        client_name=context.user_data['client_name'],
        amount=context.user_data['amount'],
        due_date=context.user_data['due_date'],
        notes=context.user_data.get('notes')
    )
    
    success_msg = f"""✅ **Invoice Created!**

**#{invoice_id}** {context.user_data['client_name']}
💵 ${context.user_data['amount']:.2f}
📅 Due: {context.user_data['due_date']}
"""
    
    if context.user_data.get('notes'):
        success_msg += f"📝 {context.user_data['notes']}\n"
    
    success_msg += f"\nUse /list to view all invoices."
    
    await update.message.reply_text(success_msg, parse_mode='Markdown')
    
    # Clear conversation data
    context.user_data.clear()
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("❌ Invoice creation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

# === MAIN APPLICATION ===

def main():
    """Start the bot"""
    # Initialize database
    db.init_db()
    
    # Create application
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Conversation handler for creating invoices
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('new', new_invoice_start)],
        states={
            CLIENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_client_name)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
            DUE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_due_date)],
            NOTES: [
                CommandHandler('skip', skip_notes),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_notes)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Add handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('list', list_invoices))
    app.add_handler(CommandHandler('all', all_invoices))
    app.add_handler(CommandHandler('stats', stats_command))
    app.add_handler(CommandHandler('account', account_command))
    app.add_handler(CommandHandler('upgrade', upgrade_command))
    app.add_handler(CommandHandler('paid', mark_paid))
    app.add_handler(CommandHandler('delete', delete_invoice_cmd))
    app.add_handler(conv_handler)
    
    # Start bot
    logger.info("🚀 PayTrackBot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
