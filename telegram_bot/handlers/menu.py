"""
Menu and navigation handlers for the Caucasian Trail Telegram Bot
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import MENU, CREATE_DAY, UPDATE_ID, GET_ID, DELETE_ID
from models import current_position
from utils import get_text


async def menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu choice"""
    choice = update.message.text.strip()

    if choice == '1':
        await update.message.reply_text(get_text(context, 'create_start'))
        return CREATE_DAY
    elif choice == '2':
        await update.message.reply_text(get_text(context, 'update_start'))
        return UPDATE_ID
    elif choice == '3':
        await update.message.reply_text(get_text(context, 'get_start'))
        return GET_ID
    elif choice == '4':
        await update.message.reply_text(get_text(context, 'delete_start'))
        return DELETE_ID
    else:
        await update.message.reply_text(get_text(context, 'menu_invalid'))
        return MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    current_position.reset()
    await update.message.reply_text(get_text(context, 'cancelled'))
    return ConversationHandler.END


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu"""
    current_position.reset()
    await update.message.reply_text(get_text(context, 'back_to_menu'))
    return MENU
