"""
Authentication and language handlers for the Caucasian Trail Telegram Bot
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import PASSWORD, MENU, BOT_PASSWORD
from models import current_position
from utils import get_text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation and ask for password"""
    current_position.reset()
    # Set default language if not set
    if 'lang' not in context.user_data:
        context.user_data['lang'] = 'en'
    await update.message.reply_text(get_text(context, 'welcome'))
    return PASSWORD


async def set_language_en(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Switch to English"""
    context.user_data['lang'] = 'en'
    await update.message.reply_text(get_text(context, 'lang_switched'))


async def set_language_ru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Switch to Russian"""
    context.user_data['lang'] = 'ru'
    await update.message.reply_text(get_text(context, 'lang_switched'))


async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify password and show menu"""
    password = update.message.text.strip()

    if password == BOT_PASSWORD:
        await update.message.reply_text(get_text(context, 'access_granted'))
        return MENU
    else:
        await update.message.reply_text(get_text(context, 'wrong_password'))
        return ConversationHandler.END
