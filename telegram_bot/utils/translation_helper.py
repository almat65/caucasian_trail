"""
Translation utilities for the Caucasian Trail Telegram Bot
"""

from telegram.ext import ContextTypes
from translations import TRANSLATIONS


def get_text(context: ContextTypes.DEFAULT_TYPE, key: str, **kwargs) -> str:
    """Get translated text based on user's language preference"""
    lang = context.user_data.get('lang', 'en')
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS['en'][key])
    return text.format(**kwargs) if kwargs else text
