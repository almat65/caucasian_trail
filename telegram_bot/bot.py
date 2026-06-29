#!/usr/bin/env python3
"""
Telegram bot to update actual position on the Caucasian Trail map
Fetches actual_position.geojson from GitHub, adds new position, and commits back
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use environment variables directly

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import configuration and handlers
from config import (TELEGRAM_TOKEN, GITHUB_TOKEN, PASSWORD, MENU, GET_ID,
                   CREATE_DAY, CREATE_DATE, CREATE_LOCATION, CREATE_DISTANCE, CREATE_ELEVATION,
                   CREATE_ACCOMMODATION, CREATE_LATITUDE, CREATE_LONGITUDE, CREATE_YOUTUBE,
                   CREATE_NOTES, CREATE_PHOTOS, UPDATE_ID, UPDATE_FIELD, UPDATE_VALUE,
                   UPDATE_PHOTOS, DELETE_ID, DELETE_CONFIRM)
from handlers import (start, set_language_en, set_language_ru, check_password,
                     menu_choice, cancel, back_to_menu, get_record_by_id,
                     create_get_day, create_get_date, create_get_location,
                     create_get_distance, create_get_elevation, create_get_accommodation,
                     create_get_latitude, create_get_longitude, create_get_youtube,
                     create_get_notes, create_get_photos, update_get_id,
                     update_get_field, update_get_value, update_get_photos,
                     delete_get_id, delete_confirm)


def main():
    """Start the bot"""
    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN environment variable not set!")
        return

    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN environment variable not set!")
        return

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add language switch commands (available anytime)
    application.add_handler(CommandHandler('en', set_language_en))
    application.add_handler(CommandHandler('ru', set_language_ru))

    # Setup conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)],
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_choice)],

            # Get record
            GET_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_record_by_id)],

            # Create record
            CREATE_DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_day)],
            CREATE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_date)],
            CREATE_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_location)],
            CREATE_DISTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_distance)],
            CREATE_ELEVATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_elevation)],
            CREATE_ACCOMMODATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_accommodation)],
            CREATE_LATITUDE: [
                MessageHandler(filters.LOCATION, create_get_latitude),
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_latitude)
            ],
            CREATE_LONGITUDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_longitude)],
            CREATE_YOUTUBE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_youtube)],
            CREATE_NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_notes)],
            CREATE_PHOTOS: [
                MessageHandler(filters.PHOTO, create_get_photos),
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_photos)
            ],

            # Update record
            UPDATE_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_get_id)],
            UPDATE_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_get_field)],
            UPDATE_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_get_value)],
            UPDATE_PHOTOS: [
                MessageHandler(filters.PHOTO, update_get_photos),
                MessageHandler(filters.TEXT & ~filters.COMMAND, update_get_photos)
            ],

            # Delete record
            DELETE_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_get_id)],
            DELETE_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_confirm)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('menu', back_to_menu),
        ]
    )

    application.add_handler(conv_handler)

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
